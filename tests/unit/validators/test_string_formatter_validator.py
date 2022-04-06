import pytest

from ytdl_subscribe.validators.base.string_formatter_validators import (
    DictFormatterValidator,
)
from ytdl_subscribe.validators.base.string_formatter_validators import (
    StringFormatterValidator,
)
from ytdl_subscribe.validators.exceptions import StringFormattingException
from ytdl_subscribe.validators.exceptions import ValidationException


@pytest.fixture
def error_message_unequal_brackets_str():
    return (
        "Brackets are reserved for {variable_names} and "
        "should contain a single open and close bracket."
    )


@pytest.fixture
def error_message_unequal_regex_matches_str():
    return (
        "{variable_names} should only contain lowercase letters and "
        "underscores with a single open and close bracket."
    )


class TestStringFormatterValidator(object):
    def test_parse(self):
        format_string = "Here is my {var_one} and {var_two} 💩"
        validator = StringFormatterValidator(
            name="test_format_variables", value=format_string
        )

        assert validator.format_string == format_string
        assert validator.format_variables == ["var_one", "var_two"]

    def test_format_variables(self):
        format_string = "No vars 💩"
        assert (
            StringFormatterValidator(
                name="test_format_variables_empty", value=format_string
            ).format_variables
            == []
        )

    @pytest.mark.parametrize(
        "format_string",
        [
            "Try {var_one{ and {var_two}",
            "Single open {",
            "Single close }",
            "Try }var_one} and {var_one}",
        ],
    )
    def test_validate_fail_uneven_brackets(
        self, format_string, error_message_unequal_brackets_str
    ):
        expected_error_msg = (
            f"Validation error in fail: {error_message_unequal_brackets_str}"
        )

        with pytest.raises(ValidationException, match=expected_error_msg):
            _ = StringFormatterValidator(name="fail", value=format_string)

    @pytest.mark.parametrize(
        "format_string",
        [
            "Try {var1} numbers",
            "Try {VAR1} caps w/numbers",
            "Try {internal{bracket}}",
            "Try }backwards{ facing",
            "Try {var_1}}{",
            "Try {} empty",
        ],
    )
    def test_validate_fail_bad_variable(
        self, format_string, error_message_unequal_regex_matches_str
    ):
        expected_error_msg = (
            f"Validation error in fail: {error_message_unequal_regex_matches_str}"
        )

        with pytest.raises(ValidationException, match=expected_error_msg):
            _ = StringFormatterValidator(name="fail", value=format_string)

    @pytest.mark.parametrize(
        "format_string, bad_variable",
        [
            ("keyword {while}", "while"),
            ("{try} {valid_var}", "try"),
        ],
    )
    def test_validate_fail_variable_keyword_or_not_identifier(
        self, format_string, bad_variable
    ):
        expected_error_msg = (
            f"Validation error in fail: "
            f"'{bad_variable}' is a Python keyword and cannot be used as a variable."
        )

        with pytest.raises(ValidationException, match=expected_error_msg):
            _ = StringFormatterValidator(name="fail", value=format_string)

    def test_string_formatter_single_field(self):
        uid = "this uid"
        format_string = StringFormatterValidator(
            name="test", value=f"prefix {{uid}} suffix"
        )
        expected_string = f"prefix {uid} suffix"

        assert (
            format_string.apply_formatter(variable_dict={"uid": uid}) == expected_string
        )

    def test_entry_formatter_duplicate_fields(self):
        upload_year = "2022"
        format_string = StringFormatterValidator(
            name="test", value=f"prefix {{upload_year}} {{upload_year}} suffix"
        )
        expected_string = f"prefix {upload_year} {upload_year} suffix"

        assert (
            format_string.apply_formatter(variable_dict={"upload_year": upload_year})
            == expected_string
        )

    def test_entry_formatter_override_recursive(self):
        variable_dict = {
            "level_a": "level a",
            "level_b": "level b and {level_a}",
            "level_c": "level c and {level_b}",
        }

        format_string = StringFormatterValidator(
            name="test", value="level d and {level_c}"
        )
        expected_string = "level d and level c and level b and level a"

        assert (
            format_string.apply_formatter(variable_dict=variable_dict)
            == expected_string
        )

    def test_entry_formatter_override_recursive_fail_cycle(self):
        variable_dict = {
            "level_a": "{level_b}",
            "level_b": "{level_a}",
        }

        # Max depth is 3 so should go level_a -(0)-> level_b -(1)-> level_a -(2)-> level_b
        expected_error_msg = (
            "Validation error in test: Attempted to format but failed after reaching max recursion "
            "depth of 3. Try to keep variables dependent on only one other variable at max. "
            "Unresolved variables: level_b"
        )

        format_string = StringFormatterValidator(name="test", value="{level_a}")

        with pytest.raises(StringFormattingException, match=expected_error_msg):
            _ = format_string.apply_formatter(variable_dict=variable_dict)


class TestDictFormatterValidator(object):
    def test_validates_values(self):
        key1_format_string = "string with {variable}"
        key2_format_string = "no variables"
        validator = DictFormatterValidator(
            name="validator",
            value={"key1": key1_format_string, "key2": key2_format_string},
        )

        assert validator.dict["key1"].format_string == key1_format_string
        assert validator.dict["key2"].format_string == key2_format_string

        assert validator.dict["key1"].format_variables == ["variable"]
        assert validator.dict["key2"].format_variables == []
