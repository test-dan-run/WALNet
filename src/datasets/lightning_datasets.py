import os
import json
from typing import Optional
from omegaconf import DictConfig
import pytorch_lightning as pl
from torch.utils.data import DataLoader

from src.datasets.core.audioset import AudioSetDataset

class LightningAudioSetDataset(pl.LightningDataModule):
    def __init__(self, dataset_cfg: DictConfig, batch_size: int = 32):

        super(LightningAudioSetDataset, self).__init__()
        self.cfg = dataset_cfg
        self.batch_size = batch_size

        with open(self.cfg.labels_indices_path, mode='r', encoding='utf-8') as fr:
            lines = fr.readlines()
        # [[idx1, AudioSetlabel1, Textlabel1], [idx2, AudioSetlabel2, Textlabel2], ...]
        self.labels_list = [line.strip('\n').split(',', 2) for line in lines]
        self.nclass = len(self.labels_list)

    @staticmethod
    def update_manifest_audiopaths(path: str) -> str:

        manifest_dir = os.path.dirname(path)
        with open(path, mode='r', encoding='utf-8') as fr:
            lines = fr.readlines()
        items = [json.loads(line.strip('\r\n')) for line in lines]
        # append manifest_dir to audiopath
        for item in items:
            item['audio_filepath'] = os.path.join(manifest_dir, item['audio_filepath'])
        
        output_filename = f'updated_{os.path.basename(path)}'
        output_path = os.path.join(manifest_dir, output_filename)
        with open(output_path, mode='w', encoding='utf-8') as fw:
            for item in items:
                fw.write(json.dumps(item)+'\n')

        return output_path

    def prepare_data(self):
        
        # change audio filepaths from relative to absolute paths
        self.cfg.train_manifest_path = LightningAudioSetDataset.update_manifest_audiopaths(self.cfg.train_manifest_path)
        self.cfg.valid_manifest_path = LightningAudioSetDataset.update_manifest_audiopaths(self.cfg.valid_manifest_path)
        if self.cfg.test_manifest_path:
            self.cfg.test_manifest_path = LightningAudioSetDataset.update_manifest_audiopaths(self.cfg.test_manifest_path)

    def setup(self, stage: Optional[str] = None):
        if stage in (None, 'fit'):
            self.train_data = AudioSetDataset(
                manifest_path = self.cfg.train_manifest_path, 
                labels_list = self.labels_list, 
                sample_rate = self.cfg.sample_rate, 
                n_fft = self.cfg.n_fft, 
                hop_length = self.cfg.hop_length, 
                power = self.cfg.power, 
                num_mels = self.cfg.num_mels, 
                audio_length_sec = self.cfg.audio_length_sec, 
                random_seed = self.cfg.random_seed,
            )

            self.valid_data = AudioSetDataset(
                manifest_path = self.cfg.valid_manifest_path, 
                labels_list = self.labels_list, 
                sample_rate = self.cfg.sample_rate, 
                n_fft = self.cfg.n_fft, 
                hop_length = self.cfg.hop_length, 
                power = self.cfg.power, 
                num_mels = self.cfg.num_mels, 
                audio_length_sec = self.cfg.audio_length_sec, 
                random_seed = self.cfg.random_seed,
            )

        if stage == 'test':
            self.test_data = AudioSetDataset(
                manifest_path = self.cfg.test_manifest_path, 
                labels_list = self.labels_list, 
                sample_rate = self.cfg.sample_rate, 
                n_fft = self.cfg.n_fft, 
                hop_length = self.cfg.hop_length, 
                power = self.cfg.power, 
                num_mels = self.cfg.num_mels, 
                audio_length_sec = self.cfg.audio_length_sec, 
                random_seed = self.cfg.random_seed,
            )

    def train_dataloader(self):
        return DataLoader(self.train_data, shuffle=True, batch_size=self.batch_size)

    def val_dataloader(self):
        return DataLoader(self.valid_data, shuffle=False, batch_size=self.batch_size)

    def test_dataloader(self):
        return DataLoader(self.test_data, shuffle=False, batch_size=self.batch_size)
