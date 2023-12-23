import torch.nn as nn
import torch

class Generator_x(nn.Module):
    def __init__(self):
        super(Generator_x, self).__init__()
        self.time_ser_emd = nn.LSTM(input_size=95, hidden_size=30, num_layers=1, batch_first=True)
        # spatial embeddings
        self.node_emb = nn.Parameter(torch.empty(95, 30))
        nn.init.xavier_uniform_(self.node_emb)
        # temporal embeddings
        self.time_emb = nn.Parameter(torch.empty(30, 30))
        nn.init.xavier_uniform_(self.time_emb)
        self.encode=nn.LSTM(input_size=155, hidden_size=128, num_layers=2, batch_first=True)
        self.main = nn.Sequential(
        #     nn.Linear(opt.latent_dim, 32),
        #     nn.ReLU(),
            nn.Linear(128, 100),
            nn.BatchNorm1d(30, eps=0.001, momentum=0.01),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(100, 95),
            nn.Sigmoid()
        )


    def forward(self, x,up):
        time_series_emb, (h, c) = self.time_ser_emd(x)
        if(up==1):
            node_emb=self.node_emb.unsqueeze(0).expand(64,-1,-1)
            time_emb=self.time_emb.unsqueeze(0).expand(64, -1, -1)
        else:
            node_emb = self.node_emb.unsqueeze(0).expand(1, -1, -1)
            time_emb = self.time_emb.unsqueeze(0).expand(1, -1, -1)
        # concate embedings
        hidden = torch.cat((time_series_emb ,node_emb ,time_emb), dim=1)
        hidden=hidden.transpose(1,2)
        out, (h, c)=self.encode(hidden)
        out=self.main(out)
        return out



class Encoder_x(nn.Module):

    def __init__(self):
        super(Encoder_x, self).__init__()
        self.lstm = nn.LSTM(input_size=95, hidden_size=128, num_layers=2, batch_first=True)
        self.main = nn.Sequential(
            nn.Linear(128, 100),
            nn.BatchNorm1d(30, eps=0.001, momentum=0.01),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(100, 95),
            nn.Tanh()
        )

    def forward(self, x):
        out, (h, c) = self.lstm(x)
        out = self.main(out)
        return out

class Discriminator_x(nn.Module):
    def __init__(self):
        super(Discriminator_x, self).__init__()
        self.conv1 = nn.Sequential(
            nn.LSTM(input_size=95, hidden_size=64, num_layers=1, batch_first=True)
        )
        self.conv2 = nn.Sequential(
            nn.LSTM(input_size=95, hidden_size=64, num_layers=1, batch_first=True)
        )
        self.conv4 = nn.Sequential(
            nn.Linear(128, 64),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(64, 32),
            nn.BatchNorm1d(30),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

    def forward(self, x,z):
        x_out,(h, c)=self.conv1(x)
        z_out,(h, c) = self.conv2(z)
        out=torch.cat([x_out, z_out], dim=2)
        # out = self.conv3(out)
        out=self.conv4(out)
        return out
class Discriminator_i(nn.Module):
    def __init__(self):
        super(Discriminator_i, self).__init__()

        self.conv1 = nn.Sequential(
            nn.LSTM(input_size=95, hidden_size=128, num_layers=2, batch_first=True)
        )

        self.conv4 = nn.Sequential(
            nn.Linear(128, 100),
            nn.BatchNorm1d(30),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(100, 95),
            nn.Sigmoid()
        )

    def forward(self,x):
        x_out, (h, c) = self.conv1(x)
        out = self.conv4(x_out)
        return out



