import os
import sys
import json
import yt_dlp
import subprocess
from tqdm import tqdm
from multiprocessing import Pool
from typing import Union, List

class DownloadAudioSet:
	def __init__(
		self, output_dir: str, csv_filepath: str, default_url: str = 'https://www.youtube.com/watch?v=', preftype: str = 'm4a',
		num_channels: int = 1, sample_rate: int = 44100, bit_rate: int = 16,
		create_manifest: bool = True, manifest_filename: str = 'manifest.json'
		) -> None:

		self.csv_filepath = csv_filepath

		csv_filename = os.path.basename(csv_filepath)
		self.output_dir = os.path.join(output_dir, os.path.splitext(csv_filename)[0])
		
		self.default_url = default_url
		self.preftype = preftype

		self.num_channels = num_channels
		self.sample_rate = sample_rate
		self.bit_rate = bit_rate

		self.create_manifest = create_manifest
		self.manifest_filepath = os.path.join(self.output_dir, manifest_filename)
		if os.path.exists(self.manifest_filepath):
			os.remove(self.manifest_filepath)

	def update_manifest(self, path: str, duration: Union[int, float], labels: List[str]) -> None:

		item = {
			'audio_filepath': path,
			'duration': duration,
			'labels': labels,
			}

		with open(self.manifest_filepath, mode='a', encoding='utf-8') as fw:
			fw.write(json.dumps(item)+'\n')

	# Method to download best audio available for audio id
	# Download only the required audio segments
	def download_audio(
		self, audio_id: str, start_time: int, end_time: int,
		folder_ext: str = 'downloaded',
		) -> str:

		output_dir = os.path.join(self.output_dir, folder_ext)
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

	# Format audio - 16 bit Signed PCM audio sampled at 44.1kHz
	def format_audio(
		self, input_path: str, output_ext: str = '.wav', folder_ext: str = 'processed',
		) -> str:

		output_dir = os.path.join(self.output_dir, folder_ext)
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
		start_seconds: Union[str, int, float], end_seconds: Union[str, int, float], labels: str,
		remove_downloads: bool = False
		) -> int:

		start_seconds = int(float(start_seconds))
		end_seconds = int(float(end_seconds))

		downloaded_path = self.download_audio(audio_id, start_seconds, end_seconds)
		if downloaded_path == '':
			return ''
		
		output_path = self.format_audio(downloaded_path)
		
		if remove_downloads:
			os.remove(downloaded_path)

		# generate manifest requirements
		duration = end_seconds - start_seconds
		relpath = os.path.relpath(output_path, self.output_dir)
		labels = labels.strip('\n')
		labels = labels.replace('"', '')
		labels = labels.split(',')

		self.update_manifest(relpath, duration, labels)

		return output_path

	def mp_download_and_process_audio(self, args):
		self.download_and_process_audio(*args)

	def download_dataset(
		self, num_threads: int = 1,
		) -> str:

		with open(self.csv_filepath, mode='r', encoding='utf-8') as f:
			lines = f.readlines()
			# ignore first 3 commented lines
			lines = lines[3:]

		queries = [line.split(', ') for line in lines]

		if num_threads > 1:
			P = Pool(num_threads)
			for idx in tqdm(range(0, len(queries), num_threads)):
				target_queries = queries[idx:idx+num_threads]
				P.map(self.mp_download_and_process_audio, target_queries)
		
		else:
			for idx, query in tqdm(enumerate(queries)):
				self.download_and_process_audio(*query)


if __name__ == '__main__':
	# output_dir: str, csv_filepath: str, 
	download_obj = DownloadAudioSet(output_dir=sys.argv[1], csv_filepath=sys.argv[2])
	download_obj.download_dataset(num_threads=int(sys.argv[3]))