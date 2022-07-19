
from torch import Tensor
import torch.nn as nn
import numpy as np
import torch.nn.functional as F
import torch.nn.init as init

class WALNet(nn.Module):

    def __init__(self, nclass: int):
        super(WALNet,self).__init__()

        self.globalpool = F.avg_pool2d

        self.layer1 = nn.Sequential(nn.Conv2d(1,64,kernel_size=3,padding=1),nn.BatchNorm2d(64),nn.ReLU())
        self.layer2 = nn.Sequential(nn.Conv2d(64,64,kernel_size=3,padding=1),nn.BatchNorm2d(64),nn.ReLU())
        self.layer3 = nn.MaxPool2d((1,2)) 

        self.layer4 = nn.Sequential(nn.Conv2d(64,128,kernel_size=3,padding=1),nn.BatchNorm2d(128),nn.ReLU())
        self.layer5 = nn.Sequential(nn.Conv2d(128,128,kernel_size=3,padding=1),nn.BatchNorm2d(128),nn.ReLU())
        self.layer6 = nn.MaxPool2d((1,2)) 

        self.layer7 = nn.Sequential(nn.Conv2d(128,256,kernel_size=3,padding=1),nn.BatchNorm2d(256),nn.ReLU())
        self.layer8 = nn.Sequential(nn.Conv2d(256,256,kernel_size=3,padding=1),nn.BatchNorm2d(256),nn.ReLU())
        self.layer9 = nn.MaxPool2d((1,2))

        self.layer10 = nn.Sequential(nn.Conv2d(256,512,kernel_size=3,padding=1),nn.BatchNorm2d(512),nn.ReLU())
        self.layer11 = nn.Sequential(nn.Conv2d(512,512,kernel_size=3,padding=1),nn.BatchNorm2d(512),nn.ReLU())
        self.layer12 = nn.MaxPool2d((1,2)) 

        self.layer13 = nn.Sequential(nn.Conv2d(512,1024,kernel_size=(1,8)),nn.BatchNorm2d(1024),nn.ReLU())
        self.layer14 = nn.Sequential(nn.Conv2d(1024,1024,kernel_size=1),nn.BatchNorm2d(1024),nn.ReLU())
        self.layer15 = nn.Sequential(nn.Conv2d(1024,nclass,kernel_size=1),nn.Sigmoid())
        
    def forward(self, x: Tensor):
        
        out = self.layer1(x)
        out = self.layer2(out)
        out = self.layer3(out)
        out = self.layer4(out)
        out = self.layer5(out)
        out = self.layer6(out)
        out = self.layer7(out)
        out = self.layer8(out)
        out = self.layer9(out)
        out = self.layer10(out)
        out = self.layer11(out)
        out = self.layer12(out)
        out = self.layer13(out)
        out = self.layer14(out)
        out1 = self.layer15(out)
        
        out = self.globalpool(out1,kernel_size=out1.size()[2:])
        out = out.view(out.size(0),-1)
        return out #,out1

    def xavier_init(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                init.xavier_uniform(m.weight, gain=nn.init.calculate_gain('relu'))
                m.bias.data.zero_()
            elif isinstance(m, nn.BatchNorm2d):
                m.weight.data.fill_(1)
                m.bias.data.zero_()
