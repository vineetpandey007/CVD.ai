import torch
from captum.attr import LayerIntegratedGradients


class TinyModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.embedding = torch.nn.Embedding(16, 8)
        self.head = torch.nn.Linear(8, 2)

    def forward(self, token_ids):
        return self.head(self.embedding(token_ids).mean(dim=1))


def main():
    torch.manual_seed(42)
    model = TinyModel().eval()
    input_ids = torch.tensor([[1, 4, 7, 2]], dtype=torch.long)
    baseline = torch.zeros_like(input_ids)
    lig = LayerIntegratedGradients(model, model.embedding)
    attributions, delta = lig.attribute(
        input_ids,
        baselines=baseline,
        target=1,
        n_steps=32,
        return_convergence_delta=True,
    )
    print(f"Attribution shape: {tuple(attributions.shape)}")
    print(f"Has NaN: {torch.isnan(attributions).any().item()}")
    print(f"Convergence delta: {delta.detach().cpu().item()}")


if __name__ == "__main__":
    main()
