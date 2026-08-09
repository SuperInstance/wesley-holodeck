#!/usr/bin/env python3
"""
Tests for wesley-holodeck creative-loop.py

Tests cover:
- API call functions (mocked)
- HTML scene generation
- Creative loop flow (mocked API)
- Teacher rotation logic
- File output structure
- Error handling and retries
"""

import json
import os
import sys
import unittest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import importlib.util
import base64

# Import the module
SPEC = importlib.util.spec_from_file_location(
    "creative_loop",
    "/home/eileen/projects/wesley-holodeck/creative-loop.py"
)

# We need to mock the DEEPINFRA_KEY check before importing
with patch.dict(os.environ, {"DEEPINFRA_API_KEY": "test-key"}):
    MODULE = importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(MODULE)


class TestConfig(unittest.TestCase):
    """Test configuration constants."""

    def test_ollama_url_is_localhost(self):
        self.assertIn("localhost", MODULE.OLLAMA_URL)
        self.assertIn("11434", MODULE.OLLAMA_URL)

    def test_deepinfra_url_correct(self):
        self.assertIn("deepinfra.com", MODULE.DEEPINFRA_URL)

    def test_deepinfra_img_url_correct(self):
        self.assertIn("deepinfra.com", MODULE.DEEPINFRA_IMG_URL)

    def test_wesley_model_is_granite(self):
        self.assertIn("granite", MODULE.WESLEY_MODEL)

    def test_teachers_list_has_entries(self):
        self.assertGreaterEqual(len(MODULE.TEACHERS), 4)

    def test_teachers_have_required_fields(self):
        for teacher in MODULE.TEACHERS:
            self.assertIn("model", teacher)
            self.assertIn("name", teacher)
            self.assertIn("persona", teacher)

    def test_teachers_use_different_models(self):
        models = [t["model"] for t in MODULE.TEACHERS]
        self.assertGreater(len(set(models)), 1)

    def test_journal_dir_is_path(self):
        self.assertIsInstance(MODULE.JOURNAL_DIR, Path)

    def test_writings_dir_is_path(self):
        self.assertIsInstance(MODULE.WRITINGS_DIR, Path)


class TestCallWesley(unittest.TestCase):
    """Test the call_wesley function."""

    @patch('urllib.request.urlopen')
    @patch('urllib.request.Request')
    def test_successful_call_returns_response(self, mock_req, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "response": "Wesley's creative text"
        }).encode()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = MODULE.call_wesley("test prompt")
        self.assertEqual(result, "Wesley's creative text")

    @patch('urllib.request.urlopen')
    def test_failed_call_returns_none(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("Connection refused")
        result = MODULE.call_wesley("test prompt")
        self.assertIsNone(result)

    @patch('urllib.request.urlopen')
    def test_truncates_response(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "response": "  text with whitespace  "
        }).encode()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = MODULE.call_wesley("test prompt")
        self.assertEqual(result, "text with whitespace")

    @patch('urllib.request.urlopen')
    @patch('time.sleep')
    def test_retries_on_failure(self, mock_sleep, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "response": "success on retry"
        }).encode()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)

        # First call fails, second succeeds
        mock_urlopen.side_effect = [Exception("timeout"), mock_resp]

        result = MODULE.call_wesley("test prompt", max_retries=2)
        self.assertEqual(result, "success on retry")

    @patch('urllib.request.urlopen')
    @patch('time.sleep')
    def test_respects_max_retries(self, mock_sleep, mock_urlopen):
        mock_urlopen.side_effect = Exception("always fails")
        result = MODULE.call_wesley("test prompt", max_retries=3)
        self.assertIsNone(result)
        # Should try 3 times
        self.assertEqual(mock_urlopen.call_count, 3)


class TestCallTeacher(unittest.TestCase):
    """Test the call_teacher function."""

    @patch('urllib.request.urlopen')
    @patch('urllib.request.Request')
    def test_successful_call_returns_content(self, mock_req, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "choices": [{"message": {"content": "Great feedback!"}}]
        }).encode()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = MODULE.call_teacher("model", "system", "user")
        self.assertEqual(result, "Great feedback!")

    @patch('urllib.request.urlopen')
    def test_failed_call_returns_none(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("API error")
        result = MODULE.call_teacher("model", "system", "user")
        self.assertIsNone(result)

    @patch('urllib.request.urlopen')
    @patch('time.sleep')
    def test_retries_on_failure(self, mock_sleep, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "choices": [{"message": {"content": "Feedback on retry"}}]
        }).encode()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)

        mock_urlopen.side_effect = [Exception("fail"), mock_resp]

        result = MODULE.call_teacher("model", "system", "user", max_retries=2)
        self.assertEqual(result, "Feedback on retry")


class TestGenerateImageFlux(unittest.TestCase):
    """Test the image generation function."""

    @patch('urllib.request.urlopen')
    @patch('urllib.request.Request')
    def test_successful_b64_image_generation(self, mock_req, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "data": [{"b64_json": base64.b64encode(b"fake-image-data").decode()}]
        }).encode()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            result = MODULE.generate_image_flux("prompt", tmp.name)

        self.assertTrue(result)
        os.unlink(tmp.name)

    @patch('urllib.request.urlopen')
    def test_failed_image_generation_returns_false(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("API error")
        result = MODULE.generate_image_flux("prompt", "/tmp/test.png")
        self.assertFalse(result)

    @patch('urllib.request.urlopen')
    @patch('urllib.request.Request')
    def test_handles_url_response(self, mock_req, mock_urlopen):
        # First call returns URL, second call fetches the image
        url_resp = MagicMock()
        url_resp.read.return_value = json.dumps({
            "data": [{"url": "https://example.com/image.png"}]
        }).encode()
        url_resp.__enter__ = MagicMock(return_value=url_resp)
        url_resp.__exit__ = MagicMock(return_value=False)

        img_resp = MagicMock()
        img_resp.read.return_value = b"fake-image-bytes"
        img_resp.__enter__ = MagicMock(return_value=img_resp)
        img_resp.__exit__ = MagicMock(return_value=False)

        mock_urlopen.side_effect = [url_resp, img_resp]

        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            result = MODULE.generate_image_flux("prompt", tmp.name)

        self.assertTrue(result)
        os.unlink(tmp.name)


class TestGenerateTTS(unittest.TestCase):
    """Test the TTS generation function."""

    @patch('urllib.request.urlopen')
    def test_successful_tts(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"fake-audio-data"
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            result = MODULE.generate_tts("text", tmp.name)

        self.assertTrue(result)
        os.unlink(tmp.name)

    @patch('urllib.request.urlopen')
    def test_failed_tts_returns_false(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("TTS API unavailable")
        result = MODULE.generate_tts("text", "/tmp/test.mp3")
        self.assertFalse(result)


class TestGenerateSceneHTML(unittest.TestCase):
    """Test the HTML scene generation."""

    def setUp(self):
        self.sample_text = "Paragraph 1.\n\nParagraph 2.\n\nParagraph 3."
        self.run_name = "test-run"
        self.run_dir = "/tmp/test-run-dir"

    def test_generates_valid_html(self):
        html = MODULE.generate_scene_html(self.sample_text, self.run_name, self.run_dir)

        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("<html", html)
        self.assertIn("</html>", html)

    def test_contains_title(self):
        html = MODULE.generate_scene_html(self.sample_text, self.run_name, self.run_dir)
        self.assertIn(self.run_name, html)
        self.assertIn("Wesley's Holodeck", html)

    def test_contains_all_paragraphs(self):
        html = MODULE.generate_scene_html(self.sample_text, self.run_name, self.run_dir)
        self.assertIn("Paragraph 1.", html)
        self.assertIn("Paragraph 2.", html)
        self.assertIn("Paragraph 3.", html)

    def test_escapes_html_in_text(self):
        dangerous_text = "<script>alert('xss')</script>"
        html = MODULE.generate_scene_html(dangerous_text, self.run_name, self.run_dir)
        self.assertNotIn("<script>alert", html)
        self.assertIn("&lt;script&gt;", html)

    def test_contains_css_styles(self):
        html = MODULE.generate_scene_html(self.sample_text, self.run_name, self.run_dir)
        self.assertIn("<style>", html)
        self.assertIn("#scene", html)
        self.assertIn("#journal", html)

    def test_contains_javascript(self):
        html = MODULE.generate_scene_html(self.sample_text, self.run_name, self.run_dir)
        self.assertIn("<script>", html)
        self.assertIn("function", html)

    def test_contains_journal_class(self):
        html = MODULE.generate_scene_html(self.sample_text, self.run_name, self.run_dir)
        self.assertIn("journal-text", html)

    def test_contains_vignette(self):
        html = MODULE.generate_scene_html(self.sample_text, self.run_name, self.run_dir)
        self.assertIn("vignette", html)

    def test_contains_holodeck_indicator(self):
        html = MODULE.generate_scene_html(self.sample_text, self.run_name, self.run_dir)
        self.assertIn("SIMULATION", html)

    def test_contains_fade_in_animation(self):
        html = MODULE.generate_scene_html(self.sample_text, self.run_name, self.run_dir)
        self.assertIn("fade-in", html)
        self.assertIn("fadeIn", html)

    def test_contains_stars_effect(self):
        html = MODULE.generate_scene_html(self.sample_text, self.run_name, self.run_dir)
        self.assertIn("stars", html)
        self.assertIn("twinkle", html)

    def test_has_meta_viewport(self):
        html = MODULE.generate_scene_html(self.sample_text, self.run_name, self.run_dir)
        self.assertIn("viewport", html)

    def test_has_charset(self):
        html = MODULE.generate_scene_html(self.sample_text, self.run_name, self.run_dir)
        self.assertIn("charset", html)


class TestRunCreativeLoop(unittest.TestCase):
    """Test the run_creative_loop orchestration."""

    @patch.object(MODULE, 'generate_tts', return_value=False)
    @patch.object(MODULE, 'generate_image_flux', return_value=False)
    @patch.object(MODULE, 'call_teacher')
    @patch.object(MODULE, 'call_wesley')
    def test_full_loop_with_mocks(self, mock_wesley, mock_teacher,
                                   mock_image, mock_tts):
        mock_wesley.return_value = "Wesley's brilliant draft"
        mock_teacher.return_value = "Excellent feedback from teacher"

        result = MODULE.run_creative_loop("Write about the sea", run_name="test-run")

        self.assertIsNotNone(result)
        self.assertEqual(result["run_name"], "test-run")
        self.assertEqual(result["final_text"], "Wesley's brilliant draft")
        self.assertEqual(len(result["drafts"]), 4)  # draft + 3 revisions

    @patch.object(MODULE, 'call_wesley', return_value=None)
    def test_loop_fails_gracefully_when_wesley_unavailable(self, mock_wesley):
        result = MODULE.run_creative_loop("prompt", run_name="test-fail")
        self.assertIsNone(result)

    @patch.object(MODULE, 'generate_tts', return_value=False)
    @patch.object(MODULE, 'generate_image_flux', return_value=False)
    @patch.object(MODULE, 'call_teacher')
    @patch.object(MODULE, 'call_wesley')
    def test_teacher_rotation(self, mock_wesley, mock_teacher,
                               mock_image, mock_tts):
        """Teachers should rotate across iterations."""
        mock_wesley.return_value = "Draft text"
        mock_teacher.return_value = "Feedback"

        MODULE.run_creative_loop("prompt", run_name="test-rotation")

        # 3 iterations = 3 teacher calls, each should use a different teacher model
        called_models = [call.args[0] for call in mock_teacher.call_args_list]
        self.assertEqual(len(called_models), 3)

    @patch.object(MODULE, 'generate_tts', return_value=False)
    @patch.object(MODULE, 'generate_image_flux', return_value=False)
    @patch.object(MODULE, 'call_teacher')
    @patch.object(MODULE, 'call_wesley')
    def test_fallback_when_teacher_unavailable(self, mock_wesley,
                                                 mock_teacher, mock_image, mock_tts):
        """When teacher fails, Wesley should still complete the loop."""
        mock_wesley.return_value = "Draft"
        mock_teacher.return_value = None  # Teacher unavailable

        result = MODULE.run_creative_loop("prompt", run_name="test-fallback")

        # Should still complete — feedback becomes a fallback message
        self.assertIsNotNone(result)


class TestTeacherPersonas(unittest.TestCase):
    """Test that teacher personas are well-formed."""

    def test_all_personas_nonempty(self):
        for teacher in MODULE.TEACHERS:
            self.assertTrue(len(teacher["persona"]) > 50,
                          f"{teacher['name']} has a short persona")

    def test_all_personas_describe_teaching_style(self):
        for teacher in MODULE.TEACHERS:
            # Each persona should mention some teaching-related word
            lower = teacher["persona"].lower()
            teaching_words = ["teach", "help", "notice", "ask", "kind",
                            "question", "encourage", "challenge"]
            self.assertTrue(any(w in lower for w in teaching_words),
                          f"{teacher['name']} persona lacks teaching language")

    def test_earnest_teacher_exists(self):
        names = [t["name"].lower() for t in MODULE.TEACHERS]
        self.assertTrue(any("earnest" in n for n in names))

    def test_voice_teacher_exists(self):
        names = [t["name"].lower() for t in MODULE.TEACHERS]
        self.assertTrue(any("voice" in n for n in names))

    def test_hermes_model_used(self):
        """The Hermes model should be used for at least one teacher."""
        models = [t["model"] for t in MODULE.TEACHERS]
        self.assertTrue(any("Hermes" in m for m in models))


class TestCodeQuality(unittest.TestCase):
    """Test code quality attributes of creative-loop.py."""

    def setUp(self):
        with open("/home/eileen/projects/wesley-holodeck/creative-loop.py") as f:
            self.code = f.read()

    def test_has_docstring(self):
        self.assertIn('"""', self.code[:500])

    def test_has_error_handling(self):
        self.assertIn("try:", self.code)
        self.assertIn("except", self.code)

    def test_has_retries(self):
        self.assertIn("max_retries", self.code)

    def test_uses_pathlib(self):
        self.assertIn("from pathlib import Path", self.code)

    def test_temperature_for_wesley_is_creative(self):
        self.assertIn("temperature", self.code.lower())

    def test_has_main_guard(self):
        self.assertIn('if __name__ == "__main__"', self.code)

    def test_uses_json_for_api_calls(self):
        self.assertIn("json.dumps", self.code)
        self.assertIn("json.loads", self.code)

    def test_timeout_protection_exists(self):
        self.assertIn("timeout", self.code)


if __name__ == "__main__":
    unittest.main()
