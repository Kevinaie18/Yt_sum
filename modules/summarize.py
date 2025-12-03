"""
LLM Summarization Module

Handles transcript summarization using OpenAI API with chunking support.
"""

import os
from typing import Optional, Tuple, List
from openai import OpenAI

# Try to import streamlit for secrets (Streamlit Cloud)
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

# Fallback to dotenv for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def get_secret(key: str, default: str = None) -> Optional[str]:
    """
    Get a secret value from Streamlit secrets or environment variables.
    Streamlit Cloud uses st.secrets, local dev uses .env
    """
    # Try Streamlit secrets first (for Streamlit Cloud)
    if HAS_STREAMLIT:
        try:
            return st.secrets.get(key, None)
        except Exception:
            pass
    
    # Fallback to environment variable
    return os.getenv(key, default)

# Constants
DEFAULT_MODEL = "gpt-4o"
MAX_CHUNK_CHARS = 12000  # Conservative limit for chunking
SUMMARY_SYSTEM_PROMPT = """You are an expert analyst specializing in extracting key insights from video transcripts. 
Your summaries are concise, well-structured, and actionable.

You must format your response in the following structure:

## Executive Summary
- Provide 3-7 bullet points capturing the most important takeaways
- Each bullet should be a complete, standalone insight

## Key Points
Group the main themes or arguments logically. Use subheadings if there are distinct topics.
- Explain each key point clearly and concisely
- Include relevant context and implications

## Notable Quotes & Facts
- Include direct quotes that are particularly impactful or memorable (use quotation marks)
- Highlight specific numbers, statistics, or data points mentioned
- Provide brief context for each quote or fact

Keep your language professional and clear. Avoid filler words and repetition."""

CHUNK_SUMMARY_PROMPT = """Summarize this section of a transcript. Focus on:
1. Main points and arguments made
2. Key facts, numbers, or data mentioned
3. Notable quotes or statements
4. Important context or background information

Be thorough but concise. This summary will be combined with summaries of other sections."""

META_SUMMARY_PROMPT = """You are combining multiple section summaries from a single video transcript into one cohesive summary.

The following are summaries of different sections of the same transcript. Synthesize them into a single, well-organized summary following this exact structure:

## Executive Summary
- Provide 3-7 bullet points capturing the most important takeaways from the ENTIRE video
- Each bullet should be a complete, standalone insight

## Key Points
Group the main themes or arguments logically across all sections. Use subheadings if there are distinct topics.
- Explain each key point clearly and concisely
- Include relevant context and implications

## Notable Quotes & Facts
- Include the most impactful direct quotes from any section (use quotation marks)
- Highlight specific numbers, statistics, or data points
- Provide brief context for each

Eliminate redundancy while preserving all unique insights. Ensure the final summary reads as a cohesive whole, not as disconnected parts."""


def get_openai_client() -> Optional[OpenAI]:
    """
    Initialize and return OpenAI client.
    
    Returns:
        OpenAI client or None if API key not configured
    """
    api_key = get_secret("OPENAI_API_KEY")
    
    if not api_key:
        return None
    
    return OpenAI(api_key=api_key)


def get_model() -> str:
    """Get the configured model name."""
    return get_secret("OPENAI_MODEL", DEFAULT_MODEL)


def chunk_text(text: str, max_chars: int = MAX_CHUNK_CHARS) -> List[str]:
    """
    Split text into chunks, trying to break at sentence boundaries.
    
    Args:
        text: Full text to chunk
        max_chars: Maximum characters per chunk
        
    Returns:
        List of text chunks
    """
    if len(text) <= max_chars:
        return [text]
    
    chunks = []
    current_chunk = ""
    
    # Split by sentences (rough approximation)
    sentences = text.replace("? ", "?|").replace("! ", "!|").replace(". ", ".|").split("|")
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # If adding this sentence would exceed limit
        if len(current_chunk) + len(sentence) + 1 > max_chars:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            current_chunk = current_chunk + " " + sentence if current_chunk else sentence
    
    # Add the last chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


def summarize_chunk(client: OpenAI, chunk: str, model: str) -> Tuple[bool, str]:
    """
    Summarize a single chunk of text.
    
    Args:
        client: OpenAI client
        chunk: Text chunk to summarize
        model: Model name to use
        
    Returns:
        Tuple of (success, summary_or_error)
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": CHUNK_SUMMARY_PROMPT},
                {"role": "user", "content": chunk}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        return True, response.choices[0].message.content
        
    except Exception as e:
        return False, f"Error summarizing chunk: {str(e)}"


def create_meta_summary(client: OpenAI, chunk_summaries: List[str], model: str) -> Tuple[bool, str]:
    """
    Create a meta-summary from multiple chunk summaries.
    
    Args:
        client: OpenAI client
        chunk_summaries: List of summaries from each chunk
        model: Model name to use
        
    Returns:
        Tuple of (success, final_summary_or_error)
    """
    combined_summaries = "\n\n---\n\n".join([
        f"Section {i+1} Summary:\n{summary}" 
        for i, summary in enumerate(chunk_summaries)
    ])
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": META_SUMMARY_PROMPT},
                {"role": "user", "content": combined_summaries}
            ],
            temperature=0.3,
            max_tokens=3000
        )
        
        return True, response.choices[0].message.content
        
    except Exception as e:
        return False, f"Error creating meta-summary: {str(e)}"


def summarize_transcript(transcript: str, progress_callback=None) -> Tuple[bool, str]:
    """
    Summarize a transcript using the configured LLM.
    
    Implements chunking for long transcripts:
    1. If transcript fits in context, summarize directly
    2. If too long, chunk and summarize each, then create meta-summary
    
    Args:
        transcript: Full transcript text
        progress_callback: Optional callback function for progress updates
        
    Returns:
        Tuple of (success, summary_or_error)
    """
    # Get client
    client = get_openai_client()
    
    if not client:
        return False, "OpenAI API key not configured. Please set OPENAI_API_KEY in your environment."
    
    model = get_model()
    
    # Check if we need to chunk
    chunks = chunk_text(transcript)
    
    if len(chunks) == 1:
        # Single chunk - direct summarization
        if progress_callback:
            progress_callback("Generating summary...")
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
                    {"role": "user", "content": f"Please summarize the following transcript:\n\n{transcript}"}
                ],
                temperature=0.3,
                max_tokens=3000
            )
            
            return True, response.choices[0].message.content
            
        except Exception as e:
            error_msg = str(e)
            if "api_key" in error_msg.lower():
                return False, "Invalid OpenAI API key. Please check your configuration."
            if "rate_limit" in error_msg.lower():
                return False, "Rate limit exceeded. Please wait a moment and try again."
            if "context_length" in error_msg.lower() or "maximum context" in error_msg.lower():
                return False, "Transcript too long for the model. Try a shorter video."
            return False, f"Error calling LLM API: {error_msg}"
    
    else:
        # Multiple chunks - summarize each, then meta-summarize
        chunk_summaries = []
        
        for i, chunk in enumerate(chunks):
            if progress_callback:
                progress_callback(f"Summarizing section {i+1} of {len(chunks)}...")
            
            success, result = summarize_chunk(client, chunk, model)
            
            if not success:
                return False, result
            
            chunk_summaries.append(result)
        
        # Create meta-summary
        if progress_callback:
            progress_callback("Creating final summary...")
        
        return create_meta_summary(client, chunk_summaries, model)


def check_api_configuration() -> Tuple[bool, str]:
    """
    Check if the LLM API is properly configured.
    
    Returns:
        Tuple of (is_configured, message)
    """
    api_key = get_secret("OPENAI_API_KEY")
    
    if not api_key:
        return False, "OpenAI API key not found. Add OPENAI_API_KEY to Streamlit secrets or .env file."
    
    if api_key.startswith("sk-") or api_key.startswith("sk-proj-"):
        return True, f"OpenAI configured (model: {get_model()})"
    
    return True, f"API key configured (model: {get_model()})"

