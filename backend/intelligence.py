from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
import nltk
import re

class MeetingIntelligence:
    def __init__(self, language="english"):
        self.language = language
        # Ensure NLTK data is available
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
            
        try:
            nltk.data.find('tokenizers/punkt_tab')
        except LookupError:
             nltk.download('punkt_tab')

    def generate_summary(self, text, sentence_count=5):
        if not text or len(text.split()) < 50:
            return "Transcript too short to summarize."

        parser = PlaintextParser.from_string(text, Tokenizer(self.language))
        stemmer = Stemmer(self.language)
        summarizer = LsaSummarizer(stemmer)
        summarizer.stop_words = get_stop_words(self.language)

        summary_sentences = summarizer(parser.document, sentence_count)
        summary = " ".join([str(sentence) for sentence in summary_sentences])
        return summary

    def extract_action_items(self, text):
        action_keywords = [
            "will", "going to", "task", "follow up", "deadline", 
            "schedule", "remind", "action", "todo", "ensure", "make sure"
        ]
        
        # Split into sentences (simple split to avoid complex dep)
        sentences = re.split(r'(?<=[.!?]) +', text)
        action_items = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in action_keywords):
                # Clean up and add
                clean_sentence = sentence.strip()
                if 10 < len(clean_sentence) < 200: # Filter noise
                    action_items.append(f"- {clean_sentence}")
                    
        if not action_items:
            return "No explicit action items detected."
            
        return "\n".join(action_items)

    def generate_report(self, transcript_text, formatted_text):
        summary = self.generate_summary(transcript_text)
        actions = self.extract_action_items(transcript_text)
        
        report = f"""# Meeting Intelligence Report

## 📝 Executive Summary
{summary}

## 🚀 Action Items & Key Tasks
{actions}

## 💬 Full Transcript
{formatted_text}
"""
        return report
