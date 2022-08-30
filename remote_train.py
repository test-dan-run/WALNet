import warnings
warnings.simplefilter('ignore', UserWarning)

import hydra
from omegaconf import DictConfig

from clearml import Task, Dataset

@hydra.main(config_path='configs', config_name='remote_main')
def main(cfg: DictConfig):

    task = Task.init(
        project_name=cfg.clearml.project_name, task_name=cfg.clearml.task_name, 
        output_uri=cfg.clearml.output_uri, task_type=cfg.task_type
    )
    task.set_base_docker(cfg.clearml.base_docker_image)
    # duplicate task, reset state, and send to remote clearml agent, exit process after this
    task.execute_remotely(queue_name=cfg.clearml.queue_name, clone=False, exit_process=True)

    from pytorch_lightning import Trainer
    from pytorch_lightning.plugins import DDPPlugin
    from pytorch_lightning.callbacks import ModelCheckpoint
    from pytorch_lightning.loggers import TensorBoardLogger

    from src.datasets.lightning_datasets import LightningAudioSetDataset
    from src.orchestrator import LightningWALNet

    # setup dataset
    # TODO: clearml dataset logic

    data_module = LightningAudioSetDataset(
        cfg.dataset, batch_size=cfg.run.batch_size,
        )
    data_module.prepare_data()

    #########
    # TRAIN #
    #########

    data_module.setup(stage='fit')

    # initialise orchestrator
    cfg.model.nclass = data_module.nclass
    orchestrator = LightningWALNet(cfg.model, cfg.optim, cfg.run)

    # initialize callbacks
    checkpoint = ModelCheckpoint(monitor='valid_loss', filename='best', save_top_k=1)
    logger = TensorBoardLogger(cfg.run.logs_dir)  # logs and checkpoints will be stored in logs_dir

    # initialize Trainer
    trainer = Trainer(
        gpus=cfg.run.num_gpus, 
        callbacks=[checkpoint,], 
        logger=logger, 
        max_epochs=cfg.run.epochs, 
        accumulate_grad_batches=cfg.run.accumulate_grad_batches,
        strategy=DDPPlugin(find_unused_parameters=False) if cfg.run.num_gpus > 1 else None)

    # train
    trainer.fit(orchestrator, datamodule=data_module)

if __name__ == '__main__':
    main()