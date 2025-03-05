from django.core.management.base import BaseCommand
from django.utils.text import slugify
from quiz.models import Topic, Question, Answer
import random
import os
import re

# Try to import PDF processing library
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

class Command(BaseCommand):
    help
