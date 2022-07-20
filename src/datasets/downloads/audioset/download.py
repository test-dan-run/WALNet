#Code Contributor - Ankit Shah - ankit.tronix@gmail.com
import pafy
import subprocess
import os
import sys
from multiprocessing import Pool
from tqdm import tqdm
import yt_dlp
from typing import Union, Any, List

class DownloadAudioSet:
	def __init__(
		self, output_dir: str, default_url: str = 'https://www.youtube.com/watch?v=', preftype: str = 'm4a',
		num_channels: int = 1, sample_rate: int = 44100, bit_rate: int = 16
		) -> None:

		self.output_dir = output_dir
		
		self.default_url = default_url
		self.preftype = preftype

		self.num_channels = num_channels
		self.sample_rate = sample_rate
		self.bit_rate = bit_rate

	# Method to download best audio available for audio id
	def download_audio(
		self, audio_id: str, start_time: Union[str, float, int], end_time: Union[str, float, int],
		folder_ext: str = 'audio_downloaded',
		) -> str:

		start_time = int(float(start_time))
		end_time = int(float(end_time))

		output_dir = self.output_dir + '_' + folder_ext
		os.makedirs(output_dir, exist_ok=True)
		output_filename = f'Y{audio_id}_{start_time}_{end_time}.m4a'

		audio_url = self.default_url + audio_id
		print(f'Downloading from: {audio_url}')

		ydl_opts = {

			'paths': {'home': output_dir}, # set output dir
			'download_ranges': lambda x, y: [{'start_time': start_time, 'end_time': end_time},],
			'outtmpl': {'default': output_filename},
			'format': 'm4a/bestaudio/best',

			'postprocessors': [{  # Extract audio using ffmpeg
				'key': 'FFmpegExtractAudio',
				'preferredcodec': 'm4a',
			}]
		}

		try:
			with yt_dlp.YoutubeDL(ydl_opts) as ydl:
				error_code = ydl.download([audio_url,])
			return os.path.join(output_dir, output_filename) 

		except Exception as e:
			print(e)
			return ''

	# Trim audio based on start time and duration of audio. 
	def trim_audio(
		self, input_path: str, audio_id: str,
		start_seconds: Union[str, int, float], end_seconds: Union[str, int, float],
		folder_ext: str = 'audio_formatted_and_segmented_downloads',
		) -> str:

		start_seconds = int(float(start_seconds))
		end_seconds = int(float(end_seconds))
		duration = end_seconds - start_seconds

		output_dir = self.output_dir + '_' + folder_ext
		os.makedirs(output_dir, exist_ok=True)

		ext = os.path.splitext(input_path)[1]
		output_filename = f'Y{audio_id}_{str(start_seconds)}_{str(end_seconds)}{ext}'
		output_path = os.path.join(output_dir, output_filename)

		command = f'ffmpeg -loglevel panic -i {input_path} -ss {int(start_seconds)} -t {duration} -c copy -y {output_path}'
		subprocess.run(command.split())

		return output_path
	
	# Format audio - 16 bit Signed PCM audio sampled at 44.1kHz
	def format_audio(
		self, input_path: str, output_ext: str = '.wav', folder_ext: str = 'audio_formatted_and_segmented_downloads',
		) -> str:

		output_dir = f'{self.output_dir}_{folder_ext}'
		os.makedirs(output_dir, exist_ok=True)

		output_path = os.path.join(output_dir, os.path.basename(input_path))
		current_ext = os.path.splitext(input_path)[1]
		output_path = output_path.replace(current_ext, output_ext)

		tmp_path = output_path.replace(output_ext, f'_temp{output_ext}')
		upsample_cmd = f'ffmpeg -loglevel panic -i {input_path} -ac {self.num_channels} -ar {self.sample_rate} {tmp_path}'
		subprocess.run(upsample_cmd.split())

		bitrate_cmd = f'sox {tmp_path} -G -b {self.bit_rate} -r {self.sample_rate} {output_path}'
		subprocess.run(bitrate_cmd.split())

		os.remove(tmp_path)

		return output_path

	def download_and_process_audio(
		self, audio_id: str, 
		start_seconds: Union[str, int, float], end_seconds: Union[str, int, float], 
		remove_downloads: bool = False
		) -> int:

		downloaded_path = self.download_audio(audio_id, start_seconds, end_seconds)
		if downloaded_path == '':
			return 0
		
		# trimmed_path = self.trim_audio(downloaded_path, audio_id, start_seconds, end_seconds)
		output_path = self.format_audio(downloaded_path)
		
		if remove_downloads:
			os.remove(downloaded_path)
		return 1

	def mp_download_and_process_audio(self, args):
		self.download_and_process_audio(*args)

	def download_dataset(
		self, input_csv_path: str, num_threads: int = 1,
		) -> str:

		with open(input_csv_path, mode='r', encoding='utf-8') as f:
			lines = f.readlines()
			# ignore first 3 commented lines
			lines = lines[3:]

		queries = [line.split(', ')[:3] for line in lines]

		if num_threads > 1:
			P = Pool(num_threads)
			for idx in tqdm(range(0, len(queries), num_threads)):
				target_queries = queries[idx:idx+num_threads]
				P.map(self.mp_download_and_process_audio, target_queries)
		
		else:
			for idx, query in tqdm(enumerate(queries)):
				self.download_and_process_audio(*query)

if __name__ == '__main__':
	download_obj = DownloadAudioSet(output_dir=sys.argv[1])
	download_obj.download_dataset(sys.argv[2], int(sys.argv[3]))