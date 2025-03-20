import speech_recognition as sr
import os
import wave
import pyaudio


class SpeechRecognitionSystem:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

    def list_microphones(self):
        """List available microphones."""
        mic_list = sr.Microphone.list_microphone_names()
        if mic_list:
            print("Available Microphones:")
            for i, mic_name in enumerate(mic_list):
                print(f"{i}: {mic_name}")
        else:
            print("No microphones found.")

    def record_audio(self, duration=5, output_file="recorded.wav"):
        """Record audio from the microphone and save it to a file."""
        try:
            print("Recording audio...")
            # Ensure the output directory exists
            output_dir = os.path.dirname(output_file)
            if output_dir:  # Only create the directory if it is not empty
                os.makedirs(output_dir, exist_ok=True)

            audio_interface = pyaudio.PyAudio()
            stream = audio_interface.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=1024
            )

            frames = []
            for _ in range(0, int(44100 / 1024 * duration)):
                data = stream.read(1024)
                frames.append(data)

            print("Recording complete.")
            stream.stop_stream()
            stream.close()
            audio_interface.terminate()

            with wave.open(output_file, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(audio_interface.get_sample_size(pyaudio.paInt16))
                wf.setframerate(44100)
                wf.writeframes(b"".join(frames))

            print(f"Audio saved to {output_file}")
            return output_file
        except OSError as e:
            print(f"Error accessing microphone: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def transcribe_audio_file(self, file_path):
        """Transcribe an audio file to text."""
        try:
            with sr.AudioFile(file_path) as source:
                print("Processing audio file...")
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data)
                print("Transcription complete.")
                return text
        except FileNotFoundError:
            return "Audio file not found. Please check the file path."
        except sr.UnknownValueError:
            return "Could not understand the audio."
        except sr.RequestError as e:
            return f"API unavailable or unresponsive: {e}"

    def transcribe_live_audio(self):
        """Transcribe live audio from the microphone."""
        try:
            print("Please speak into the microphone.")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
                audio_data = self.recognizer.listen(source)
                text = self.recognizer.recognize_google(audio_data)
                print("You said:", text)
                return text
        except OSError:
            return "Microphone not accessible. Please check your device."
        except sr.UnknownValueError:
            return "Could not understand the audio."
        except sr.RequestError as e:
            return f"API unavailable or unresponsive: {e}"


if __name__ == "__main__":
    asr = SpeechRecognitionSystem()

    while True:
        print("\nChoose an option:")
        print("1. List available microphones")
        print("2. Record audio")
        print("3. Transcribe audio file")
        print("4. Transcribe live audio")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            asr.list_microphones()
        elif choice == "2":
            try:
                duration = int(input("Enter recording duration in seconds: "))
                file_name = input("Enter output file name (default: recorded.wav): ") or "recorded.wav"
                asr.record_audio(duration, file_name)
            except ValueError:
                print("Invalid input. Please enter a valid duration.")
        elif choice == "3":
            file_path = input("Enter the path to the audio file: ")
            transcription = asr.transcribe_audio_file(file_path)
            print("Transcription:", transcription)
        elif choice == "4":
            transcription = asr.transcribe_live_audio()
            print("Transcription:", transcription)
        elif choice == "5":
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")
