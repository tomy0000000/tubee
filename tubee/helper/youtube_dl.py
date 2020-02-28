"""Helper Functions to execute youtube_dl action"""
import youtube_dl


def build_service(additional_options):
    options = {
        "skip_download": True,
        "ignoreerrors": True,
        "extract_flat": True,
    }
    options.update(additional_options)
    return youtube_dl.YoutubeDL(options)


def fetch_video_metadata(video_id):
    service = build_service({"format": "best"})
    metadata = service.extract_info(video_id)
    return metadata
