from typing import Iterable, Tuple

import torch.nn as nn

from ..layer import AdapterLayer
from ..lora import Linear as LoRALinear
from ..model_mixin import ModelBaseAdaptersMixin
from ..prefix_tuning import PrefixTuningShim


class ViTSelfAttentionAdaptersMixin:
    def init_adapters(self, config):
        self.location_key = "self"

        # Wrap layers for LoRA
        self.query = LoRALinear.wrap(self.query, "selfattn", config, attn_key="q")
        self.key = LoRALinear.wrap(self.key, "selfattn", config, attn_key="k")
        self.value = LoRALinear.wrap(self.value, "selfattn", config, attn_key="v")

        self.prefix_tuning = PrefixTuningShim(self.location_key + "_prefix" if self.location_key else None, config)


class ViTIntermediateAdaptersMixin:
    def init_adapters(self, config):
        # Wrap layers for LoRA
        self.dense = LoRALinear.wrap(self.dense, "intermediate", config)


class ViTOutputAdaptersMixin:
    """Adds adapters to the ViTOutput module."""

    def init_adapters(self, config):
        self.output_adapters = AdapterLayer("output_adapter")

        # Wrap layers for LoRA
        self.dense = LoRALinear.wrap(self.dense, "output", config)


# Unlike BERT, self attention adapters are added to Layer module in ViT
class ViTLayerAdaptersMixin:
    """Adds adapters to the ViTSelfOutput module."""

    def init_adapters(self, config):
        self.attention_adapters = AdapterLayer("mh_adapter")


class ViTModelAdaptersMixin(ModelBaseAdaptersMixin):
    """Adds adapters to the ViTModel class."""

    def init_adapters(self, config):
        super().init_adapters(config)

    def iter_layers(self) -> Iterable[Tuple[int, nn.Module]]:
        for i, layer in enumerate(self.encoder.layer):
            yield i, layer