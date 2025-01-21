import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Pango, GLib

from typing import Dict, List, Tuple
import logging
import re

logger = logging.getLogger(__name__)

class MarkdownParser:
    def __init__(self):
        # Regex patterns for markdown elements
        self.patterns = {
            'header': re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE),
            'code_block': re.compile(r'```(\w*)\n(.*?)\n```', re.DOTALL),
            'inline_code': re.compile(r'`([^`]+)`'),
            'bold': re.compile(r'\*\*(.+?)\*\*'),
            'italic': re.compile(r'_(.+?)_'),
        }
        
    def parse(self, text: str) -> Tuple[str, List[Tuple[str, int, int]], Dict[int, str]]:
        logger.debug("Starting markdown parsing")
        result_text = text
        tags = []  # (tag_name, start, end)
        code_blocks = {}
        
        # First handle code blocks
        code_block_matches = list(self.patterns['code_block'].finditer(result_text))
        for match in reversed(code_block_matches):  # Process in reverse to keep positions valid
            start, end = match.span()
            lang, code = match.groups()
            line_num = result_text[:start].count('\n')
            code_blocks[line_num] = code.strip()
            # Keep the code but remove the markers
            result_text = (
                result_text[:start] + 
                '\n' + code.strip() + '\n' +
                result_text[end:]
            )
            tags.append(('code_block', start, start + len(code.strip()) + 2))
        
        # Handle headers
        for match in self.patterns['header'].finditer(result_text):
            level = len(match.group(1))
            start, end = match.span()
            tags.append((f'h{level}', start, end))
        
        # Handle inline formatting
        for pattern_name in ['bold', 'italic', 'inline_code']:
            for match in self.patterns[pattern_name].finditer(result_text):
                content = match.group(1)
                start, end = match.span()
                tag_name = 'code' if pattern_name == 'inline_code' else pattern_name
                # For inline elements, we want to keep the content but remove the markers
                result_text = (
                    result_text[:start] + 
                    content +
                    result_text[end:]
                )
                # Adjust the end position to match the content length
                tags.append((tag_name, start, start + len(content)))
        
        logger.debug("Parsed text:\n%s", result_text)
        logger.debug("Found tags: %s", tags)
        logger.debug("Found code blocks: %s", code_blocks)
        
        return result_text, tags, code_blocks

class RichTextView(Gtk.TextView):
    def __init__(self):
        super().__init__()
        self.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.set_editable(False)
        self.set_cursor_visible(False)
        self.set_left_margin(10)
        self.set_right_margin(10)
        
        self.buffer = self.get_buffer()
        self.setup_tags()
        self.code_blocks = {}
        
    def setup_tags(self):
        # Basic formatting
        self.buffer.create_tag("bold", weight=Pango.Weight.BOLD)
        self.buffer.create_tag("italic", style=Pango.Style.ITALIC)
        self.buffer.create_tag("code", 
            family="monospace",
            background="rgba(0,0,0,0.05)",
            scale=0.9
        )
        
        # Headers
        for i in range(1, 7):
            self.buffer.create_tag(
                f"h{i}", 
                weight=Pango.Weight.BOLD,
                scale=2.0 - (i * 0.2),
                pixels_above_lines=10,
                pixels_below_lines=5
            )
        
        # Code blocks
        self.buffer.create_tag(
            "code_block",
            family="monospace",
            background="rgba(0,0,0,0.05)",
            paragraph_background="rgba(0,0,0,0.05)",
            left_margin=20,
            right_margin=20,
            pixels_above_lines=5,
            pixels_below_lines=5,
            scale=0.9
        )

    def set_markdown(self, text: str):
        logger.debug("Raw input text:\n%s", text)
        
        # Parse markdown
        parser = MarkdownParser()
        formatted_text, tags, code_blocks = parser.parse(text)
        
        # Set text
        self.buffer.set_text(formatted_text)
        
        # Apply tags
        for tag_name, start, end in tags:
            if not self.buffer.get_tag_table().lookup(tag_name):
                logger.warning("Unknown tag: %s", tag_name)
                continue
            
            start_iter = self.buffer.get_iter_at_offset(start)
            end_iter = self.buffer.get_iter_at_offset(end)
            self.buffer.apply_tag_by_name(tag_name, start_iter, end_iter)
        
        # Add copy buttons for code blocks
        for line_num, code in code_blocks.items():
            self.add_copy_button(code, line_num)

    def add_copy_button(self, code: str, line_start: int):
        button = Gtk.Button(label="Copy")
        button.get_style_context().add_class("copy-button")
        button.connect("clicked", self.on_copy_clicked, code)
        
        iter_at_line = self.buffer.get_iter_at_line(line_start)
        anchor = self.buffer.create_child_anchor(iter_at_line)
        self.add_child_at_anchor(button, anchor)
        button.show()
        
        self.code_blocks[line_start] = code

    def on_copy_clicked(self, button: Gtk.Button, code: str):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(code, -1)
        
        button.set_label("Copied!")
        def reset_label():
            button.set_label("Copy")
            return False
        GLib.timeout_add(1000, reset_label) 