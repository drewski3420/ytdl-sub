from ytdl_subscribe.downloaders.youtube_downloader import YoutubeDownloader
from ytdl_subscribe.subscriptions.subscription import Subscription
from ytdl_subscribe.validators.config.source_options.youtube_validators import (
    YoutubePlaylistSourceValidator, YoutubeChannelSourceValidator,
)
from ytdl_subscribe.validators.config.source_options.youtube_validators import (
    YoutubeVideoSourceValidator,
)


class YoutubePlaylistSubscription(Subscription[YoutubePlaylistSourceValidator]):
    def extract_info(self):
        entries = self.get_downloader(YoutubeDownloader).download_playlist(
            playlist_id=self.source_options.playlist_id.value
        )

        for entry in entries:
            self.post_process_entry(entry)


class YoutubeChannelSubscription(Subscription[YoutubeChannelSourceValidator]):
    def extract_info(self):
        entries = self.get_downloader(YoutubeDownloader).download_channel(
            channel_id=self.source_options.channel_id.value
        )

        for entry in entries:
            self.post_process_entry(entry)


class YoutubeVideoSubscription(Subscription[YoutubeVideoSourceValidator]):
    def extract_info(self):
        entry = self.get_downloader(YoutubeDownloader).download_video(
            video_id=self.source_options.video_id.value
        )

        self.post_process_entry(entry)
