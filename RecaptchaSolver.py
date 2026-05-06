import os
import urllib.request
import random
import pydub
import speech_recognition
import time
from typing import Optional
from DrissionPage import ChromiumPage

import os

# Force system PATH into Python runtime
os.environ["PATH"] = os.environ["PATH"]
from pydub import AudioSegment
class RecaptchaSolver:
    """A class to solve reCAPTCHA challenges using audio recognition."""

    # Constants
    TEMP_DIR = os.getenv("TEMP") if os.name == "nt" else "/tmp"
    TIMEOUT_STANDARD = 7
    TIMEOUT_SHORT = 1
    TIMEOUT_DETECTION = 0.05

    def __init__(self, driver: ChromiumPage) -> None:
        """Initialize the solver with a ChromiumPage driver.

        Args:
            driver: ChromiumPage instance for browser interaction
        """
        self.driver = driver

    def solveCaptcha(self) -> None:
        """Attempt to solve the reCAPTCHA challenge.

        Raises:
            Exception: If captcha solving fails or bot is detected
        """
        
        # Handle main reCAPTCHA iframe
        self.driver.wait.ele_displayed(
            "@title=reCAPTCHA", timeout=self.TIMEOUT_STANDARD
        )
        time.sleep(0.1)
        iframe_inner = self.driver("@title=reCAPTCHA")

        # Click the checkbox
        iframe_inner.wait.ele_displayed(
            ".rc-anchor-content", timeout=self.TIMEOUT_STANDARD
        )
        iframe_inner(".rc-anchor-content", timeout=self.TIMEOUT_SHORT).click()

        # Check if solved by just clicking
        if self.is_solved():
            return

        # Handle audio challenge
        iframe = self.driver("xpath://iframe[contains(@title, 'recaptcha')]")
        iframe.wait.ele_displayed(
            "#recaptcha-audio-button", timeout=self.TIMEOUT_STANDARD
        )
        iframe("#recaptcha-audio-button", timeout=self.TIMEOUT_SHORT).click()
        time.sleep(0.3)

        if self.is_detected():
            raise Exception("Captcha detected bot behavior")

        # Download and process audio
        iframe.wait.ele_displayed("#audio-source", timeout=self.TIMEOUT_STANDARD)
        src = iframe("#audio-source").attrs["src"]

        try:
            # text_response = self._process_audio_challenge(src)
            # iframe("#audio-response").input(text_response.lower())
            # iframe("#recaptcha-verify-button").click()
            # time.sleep(0.4)

            # if not self.is_solved():
            #     raise Exception("Failed to solve the captcha")
            for attempt in range(5):
                print(f"Attempt {attempt + 1}...")

                text_response = self._process_audio_challenge(src)
                print("Recognized:", text_response)

                iframe("#audio-response").clear()
                iframe("#audio-response").input(text_response.lower())
                iframe("#recaptcha-verify-button").click()
                time.sleep(1)

                if self.is_solved():
                    print("Solved!")
                    return

                # Reload new audio if not solved
                try:
                    iframe("#recaptcha-reload-button").click()
                    time.sleep(1)
                    src = iframe("#audio-source").attrs["src"]
                except Exception as reload_err:
                    print("Reload failed:", reload_err)

            # ❗ Only raise AFTER all attempts fail
            raise Exception("Failed after multiple attempts")

        except Exception as e:
            raise Exception(f"Audio challenge failed: {str(e)}")

    def _process_audio_challenge(self, audio_url: str) -> str:
        """Process the audio challenge and return the recognized text.

        Args:
            audio_url: URL of the audio file to process

        Returns:
            str: Recognized text from the audio file
        """
        mp3_path = os.path.join(self.TEMP_DIR, f"{random.randrange(1,1000)}.mp3")
        wav_path = os.path.join(self.TEMP_DIR, f"{random.randrange(1,1000)}.wav")

        try:
            urllib.request.urlretrieve(audio_url, mp3_path)
            sound = pydub.AudioSegment.from_mp3(mp3_path)
            sound.export(wav_path, format="wav")

            recognizer = speech_recognition.Recognizer()
            with speech_recognition.AudioFile(wav_path) as source:
                audio = recognizer.record(source)

            #return recognizer.recognize_google(audio)
            try:
                return recognizer.recognize_google(audio)
            except speech_recognition.UnknownValueError:
                return ""
            except speech_recognition.RequestError as e:
                raise Exception(f"API error: {e}")
            print("Recognized text:", text_response)

        finally:
            for path in (mp3_path, wav_path):
                if os.path.exists(path):
                    try:
                        os.remove(path)
                    except OSError:
                        pass

    def is_solved(self) -> bool:
        """Check if the captcha has been solved successfully."""
        try:
            return (
                "style"
                in self.driver.ele(
                    ".recaptcha-checkbox-checkmark", timeout=self.TIMEOUT_SHORT
                ).attrs
            )
        except Exception:
            return False

    def is_detected(self) -> bool:
        """Check if the bot has been detected."""
        try:
            return (
                self.driver.ele("Try again later", timeout=self.TIMEOUT_DETECTION)
                .states()
                .is_displayed
            )
        except Exception:
            return False

    def get_token(self) -> Optional[str]:
        """Get the reCAPTCHA token if available."""
        try:
            return self.driver.ele("#recaptcha-token").attrs["value"]
        except Exception:
            return None
if __name__ == "__main__":
    page = ChromiumPage()  # launch browser
    page.get("https://www.google.com/recaptcha/api2/demo")  # test page

    solver = RecaptchaSolver(page)

    try:
        solver.solveCaptcha()
        print("Captcha solved!")
    except Exception as e:
        print("Error:", e)