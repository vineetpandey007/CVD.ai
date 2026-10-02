# NLP vulnerability detection workspace

This workspace develops binary vulnerability detection on C/C++ functions,
treated as text classification of code tokens.

No result may be written in any document until it has been produced by a
script in this repository.

Install the main ML dependencies, then install Captum separately without
resolving its declared NumPy constraint:

```powershell
pip install -r ml/requirements-ml.txt
pip install --no-deps -r ml/requirements-captum.txt
```

Captum 0.8.0 declares `numpy<2.0`, while this Python 3.13 environment requires
`numpy>=2.1`. The no-dependencies install preserves the NumPy 2.x pin above.

Note: the CodeXGLUE defect-detection split is random rather than project-level,
so reported scores will be optimistic compared with a project-level split.
