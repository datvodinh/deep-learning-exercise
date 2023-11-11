import torch
import torch.nn as nn
import torch.nn.functional as F


def one_hot(labels: torch.Tensor,
            num_classes: int,
            eps: float = 1e-6
            ) -> torch.Tensor:
    r"""Converts an integer label 2D tensor to a one-hot 3D tensor.
        Label: (N, H, W) -> Onehot: (N, C, H, W)
    """
    batch_size, height, width = labels.shape
    one_hot = torch.zeros(batch_size, num_classes, height, width).to(labels.device)
    return one_hot.scatter_(1, labels.unsqueeze(1), 1.0) + eps


class DiceLoss(nn.Module):
    def __init__(self, weights=torch.Tensor([[0.33, 0.34, 0.33]])) -> None:
        super(DiceLoss, self).__init__()
        self.eps: float = 1e-6
        self.weights: torch.Tensor = weights

    def forward(
            self,
            inputs: torch.Tensor,
            targets: torch.Tensor) -> torch.Tensor:
        # compute softmax over the classes axis
        input_soft = F.softmax(inputs, dim=1)

        # create the labels one hot tensor
        target_one_hot = one_hot(targets, num_classes=inputs.shape[1])

        # compute the actual dice score
        dims = (2, 3)
        intersection = torch.sum(input_soft * target_one_hot, dims)
        cardinality = torch.sum(input_soft + target_one_hot, dims)

        dice_score = 2. * intersection / (cardinality + self.eps)

        dice_score = torch.sum(
            dice_score * self.weights.to(dice_score.device),
            dim=1
        )

        return torch.mean(1. - dice_score), dice_score.mean().detach()
