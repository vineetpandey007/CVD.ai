# Model card

## Checkpoint

The current default checkpoint is
`mrm8488/codebert-base-finetuned-detect-insecure-code`. It is loaded as
provided, without training or fine-tuning in this project.

## Limitations

Empirical testing during development used four fixtures (two vulnerable and
two safe) across two languages. This checkpoint predicted **vulnerable** with
approximately 99% confidence regardless of the input content, while logits
varied by less than 0.1 across genuinely different code. In these tests, it
therefore provided little independent discriminative signal beyond a constant
prior.

A Devign-trained alternative checkpoint showed the identical pattern during
testing. Bandit and Semgrep are therefore the primary reliable signals in the
current build. The model currently contributes a confidence score that should
be weighted accordingly until a better checkpoint or a custom fine-tune is
available.

Raw debug output confirmed that Semgrep's free Community ruleset ran 153
rules against `examples/vulnerable_samples/sql_injection.py` and returned
zero findings without errors. Bandit reliably flags this reference SQL
injection example; Semgrep does not. The dual-signal design still holds
architecturally, but Bandit is the confirmed static-analysis signal for this
specific example.