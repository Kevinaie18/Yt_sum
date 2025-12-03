"""
YouTube Transcript Extraction Module

Handles fetching transcripts from YouTube videos using youtube-transcript-api.
"""

import re
from typing import Optional, Tuple
from youtube_transcript_api import YouTubeTranscriptApi

# Import exceptions - handle different package versions
try:
    # Newer versions (0.6.3+)
    from youtube_transcript_api._errors import (
        TranscriptsDisabled,
        NoTranscriptFound,
        VideoUnavailable,
        NoTranscriptAvailable,
    )
except ImportError:
    try:
        # Alternative import path
        from youtube_transcript_api import (
            TranscriptsDisabled,
            NoTranscriptFound,
            VideoUnavailable,
            NoTranscriptAvailable,
        )
    except ImportError:
        # Fallback: define as generic exceptions
        TranscriptsDisabled = Exception
        NoTranscriptFound = Exception
        VideoUnavailable = Exception
        NoTranscriptAvailable = Exception


def extract_video_id(url: str) -> Optional[str]:
    """
    Extract the video ID from a YouTube URL.
    
    Supports formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - https://www.youtube.com/v/VIDEO_ID
    
    Args:
        url: YouTube URL string
        
    Returns:
        Video ID string or None if not found
    """
    if not url or not isinstance(url, str):
        return None
    
    url = url.strip()
    
    # Pattern for standard youtube.com/watch?v= URLs
    standard_pattern = r'(?:youtube\.com\/watch\?v=|youtube\.com\/watch\?.+&v=)([a-zA-Z0-9_-]{11})'
    
    # Pattern for youtu.be short URLs
    short_pattern = r'youtu\.be\/([a-zA-Z0-9_-]{11})'
    
    # Pattern for embed URLs
    embed_pattern = r'youtube\.com\/embed\/([a-zA-Z0-9_-]{11})'
    
    # Pattern for /v/ URLs
    v_pattern = r'youtube\.com\/v\/([a-zA-Z0-9_-]{11})'
    
    for pattern in [standard_pattern, short_pattern, embed_pattern, v_pattern]:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def validate_youtube_url(url: str) -> Tuple[bool, str, Optional[str]]:
    """
    Validate a YouTube URL and extract video ID.
    
    Args:
        url: YouTube URL string
        
    Returns:
        Tuple of (is_valid, message, video_id)
    """
    if not url or not url.strip():
        return False, "Please enter a YouTube URL.", None
    
    url = url.strip()
    
    # Check if it looks like a YouTube URL
    if not any(domain in url.lower() for domain in ['youtube.com', 'youtu.be']):
        return False, "This doesn't appear to be a YouTube URL.", None
    
    video_id = extract_video_id(url)
    
    if not video_id:
        return False, "Could not extract video ID from URL. Please check the URL format.", None
    
    return True, "Valid YouTube URL.", video_id


def fetch_transcript(video_id: str, languages: list = None) -> Tuple[bool, str, Optional[str]]:
    """
    Fetch the transcript for a YouTube video.
    
    Args:
        video_id: YouTube video ID
        languages: List of language codes to try (default: ['en', 'en-US', 'en-GB'])
        
    Returns:
        Tuple of (success, message_or_error, transcript_text)
    """
    if languages is None:
        languages = ['en', 'en-US', 'en-GB']
    
    try:
        # Try to get transcript in preferred languages
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        transcript = None
        
        # First, try to find a manual transcript in preferred languages
        try:
            transcript = transcript_list.find_manually_created_transcript(languages)
        except NoTranscriptFound:
            pass
        
        # If no manual transcript, try auto-generated
        if transcript is None:
            try:
                transcript = transcript_list.find_generated_transcript(languages)
            except NoTranscriptFound:
                pass
        
        # If still nothing, get any available transcript and translate if possible
        if transcript is None:
            try:
                # Get the first available transcript
                available = list(transcript_list)
                if available:
                    transcript = available[0]
                    # Try to translate to English if it's not in English
                    if transcript.language_code not in languages:
                        try:
                            transcript = transcript.translate('en')
                        except Exception:
                            # Use original if translation fails
                            pass
            except Exception:
                pass
        
        if transcript is None:
            return False, "No transcript available for this video.", None
        
        # Fetch the actual transcript data
        transcript_data = transcript.fetch()
        
        # Concatenate text, removing timestamps
        full_text = " ".join([entry['text'] for entry in transcript_data])
        
        # Clean up the text (remove multiple spaces, normalize)
        full_text = re.sub(r'\s+', ' ', full_text).strip()
        
        return True, f"Transcript fetched successfully ({len(full_text):,} characters).", full_text
        
    except TranscriptsDisabled:
        return False, "Transcripts are disabled for this video.", None
    except VideoUnavailable:
        return False, "This video is unavailable (private, deleted, or region-restricted).", None
    except NoTranscriptAvailable:
        return False, "No transcript available for this video.", None
    except Exception as e:
        error_msg = str(e)
        if "Video unavailable" in error_msg:
            return False, "This video is unavailable (private, deleted, or region-restricted).", None
        return False, f"Error fetching transcript: {error_msg}", None


def get_transcript(url: str) -> Tuple[bool, str, Optional[str], Optional[str]]:
    """
    Main function to get transcript from a YouTube URL.
    
    Args:
        url: YouTube URL
        
    Returns:
        Tuple of (success, message, transcript_text, video_id)
    """
    # Validate URL
    is_valid, message, video_id = validate_youtube_url(url)
    
    if not is_valid:
        return False, message, None, None
    
    # Fetch transcript
    success, message, transcript = fetch_transcript(video_id)
    
    return success, message, transcript, video_id

