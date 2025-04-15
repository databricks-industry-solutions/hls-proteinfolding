### Protein Folding and Generative Protein Models on Databricks

The ability to computationally predict the 3D structure of proteins with near experimental accuracy is revolutionizing bioinformatics research and the way drug discovery is done. The release of AlphaFold2 by DeepMind, which won the CASP14 competition, and RoseTTAFold from the Baker Lab were the first such models to demonstrate such high performance and played a key role in the decision to award three of the researchers involved in these works the 2024 Nobel Prize in Chemistry. Many biotech and pharmaceutical organizations are using these models, including generative models for protein design, to reimagine how AI can shape their R&D businesses. Use cases include not only predicting structures to speed up analysis but also for downstream prediction of molecule properties, drug-binding, and perhaps most excitingly, generating new drugs against targets. We show how model serving, workflows, and apps on Databricks allow one to have an all-in-one platform for both protein folding and even generative protein design with a variety of cutting-edge models. These models are easy to use for both expert and wet-lab scientists and are well-governed: organizations can track how the models are used, a key consideration for data of high proprietary value.

**What's inside?** Tutorials for:

**Structure Prediction Models:**
- AlphaFold v2.3.2: uses Databricks workflows to download required datasets and can install workflows for separated CPU and GPU compute.
- ESMFold: model serving of ESMFold
- Boltz-1: Model serving of Boltz-1

**Generative Protein Modelling Tools:**
- RFDiffusion: model serving of unconditional protein generation and in-painting protein generation
- ProteinMPNN: model serving of protein sequence inference of protein backbones

**Apps:**
- Notebooks and source code to generate a protein folding app that can run model serving in real-time and submit and view AlphaFold workflow runs.

License
--------
Please see LICENSE for the details of the license. Some packages, tools, and code used inside individual tutorials are under their own licenses as described therein. Please ensure you read the details of the tutorials and licensing of individual tools. Other thrid party packages are used in tutorials within this accelerator and have their own licensing, as laid out in the table below. We note also that we made minor modifations to alphafold2 code in both the alpahfold and boltz-1 tutorials, notes on the changes made can be found in those tutorials. In the app tutorial we additionally modified examples from Modal-labs model-examples repo (MIT) for molstar viewer html construction, this is noted in the application tutorial also.

Tutorial | Package | License | Source
-------- | ------- | ------- | --------
RFDiffusion | RFDiffusion |	https://github.com/RosettaCommons/RFdiffusion?tab=License-1-ov-file#readme
RFDiffusion |Mlflow	| Apache2.0
RFDiffusion |Hydra	| MIT
RFDiffusion |OmegaConf |	BSD-3
RFDiffusion |BioPython |	https://github.com/biopython/biopython/blob/master/LICENSE.rst
RFDiffusion |DGL	| Apache2.0
RFDiffusion |pyrsistent |	MIT
RFDiffusion |e3nn	| MIT
RFDiffusion |Wandb |	MIT
RFDiffusion |Pynvml	| BSD-3
RFDiffusion |Decorator	| BSD-2
RFDiffusion |Torch |	https://github.com/pytorch/pytorch?tab=License-1-ov-file#readme
RFDiffusion |Torchvision |	BSD-3
RFDiffusion |torchaudio==0.11.0 |	BSD-2
RFDiffusion |mlflow==2.15.1	| Apache2.0
RFDiffusion |cloudpickle==2.2.1	| https://github.com/cloudpipe/cloudpickle?tab=License-1-ov-file#readme
RFDiffusion |biopython==1.79	| https://github.com/biopython/biopython/blob/master/LICENSE.rst
RFDiffusion | dllogger 	| Apache2.0 | https://github.com/NVIDIA/dllogger
RFDiffusion | SE3Transformer |	https://github.com/RosettaCommons/RFdiffusion/blob/main/env/SE3Transformer/LICENSE | https://github.com/RosettaCommons/RFdiffusion/tree/main/env/SE3Transformer
RFDiffusion | MODEL WEIGHTS |	BSD
ProteinMPNN | ProteinMPNN 	| MIT
ProteinMPNN | Numpy |	https://github.com/numpy/numpy?tab=License-1-ov-file#readme
ProteinMPNN | torch==1.11.0+cu113 |	https://github.com/pytorch/pytorch?tab=License-1-ov-file#readme
ProteinMPNN | torchvision==0.12.0+cu113 |	BSD-3
ProteinMPNN | torchaudio==0.11.0 | BSD-2
ProteinMPNN | - mlflow==2.15.1 | Apache2.0
ProteinMPNN | - cloudpickle==2.2.1 | https://github.com/cloudpipe/cloudpickle?tab=License-1-ov-file#readme
ProteinMPNN | - biopython==1.79 | https://github.com/biopython/biopython/blob/master/LICENSE.rst
ProteinMPNN | nvidia::cudatoolkit=11.3	| NVIDIA-EULA
ProteinMPNN | MODEL WEIGHTS | MIT
Alphafold | AlphaFold (2.3.2) | Apache2.0
Alphafold |hmmer	| https://github.com/EddyRivasLab/hmmer/blob/master/LICENSE
Alphafold |kalign	| GPL-3
Alphafold |hhsuite	| GPL-3
Alphafold |tzdata	| MIT
Alphafold |openmm==7.5.1 |	https://github.com/openmm/openmm/blob/master/docs-source/licenses/Licenses.txt
Alphafold |pdbfixer |	https://github.com/openmm/pdbfixer/blob/master/LICENSE
Alphafold | jax==0.3.25 |	Apache2.0
Alphafold | jaxlib==0.3.25+cuda11.cudnn805 | Apache2.0
Alphafold | absl-py==1.0.0	| Apache2.0
Alphafold | biopython==1.79	| https://github.com/biopython/biopython/blob/master/LICENSE.rst
Alphafold | chex==0.0.7	| Apache2.0
Alphafold | dm-haiku==0.0.9	| Apache2.0
Alphafold | dm-tree==0.1.6	| Apache2.0
Alphafold | docker==5.0.0	| Apache2.0
Alphafold | immutabledict==2.0.0 | MIT
Alphafold | ml-collections==0.1.0 | Apache2.0
Alphafold | numpy==1.21.6 | https://github.com/numpy/numpy?tab=License-1-ov-file#readme
Alphafold | pandas==1.3.4 | BSD-3
Alphafold | protobuf==3.20.1 | https://github.com/protocolbuffers/protobuf?tab=License-1-ov-file#readme
Alphafold | scipy==1.7.0 | BSD-3
Alphafold | tensorflow-cpu==2.9.0 | Apache2.0
Alphafold | MODEL WEIGHTS | CC BY 4.0
ESMfold | ESMFold |	MIT
ESMfold | torch | https://github.com/pytorch/pytorch?tab=License-1-ov-file#readme
ESMfold | transformers | Apache2.0
ESMfold | accelerate | Apache2.0
ESMfold | MODEL WEIGHTS |MIT
Boltz-1 | Boltz-1__ |	MIT
Boltz-1 |conda-forge::packaging |Apache2.0
Boltz-1 |conda-forge::ninja | Apache2.0
Boltz-1 |torch==2.3.1+cu121 | https://github.com/pytorch/pytorch?tab=License-1-ov-file#readme
Boltz-1 |torchvision==0.18.1+cu121 | BSD-3
Boltz-1 |mlflow==2.15.1 | Apache2.0
Boltz-1 |cloudpickle==2.2.1 | https://github.com/cloudpipe/cloudpickle?tab=License-1-ov-file#readme
Boltz-1 |requests>=2.25.1 | Apache2.0
Boltz-1 |boltz==0.4.0 | MIT
Boltz-1 |databricks-vectorsearch==0.44 |	DBLicense
Boltz-1 |langchain==0.3.14 |	
Boltz-1 |rdkit | BSD-3
Boltz-1 |absl-py==1.0.0 |	Apache2.0
Boltz-1 |transformers>=4.41 | 	Apache2.0
Boltz-1 |sentence-transformers>=2.7 |	Apache2.0
Boltz-1 |pyspark |	Apache2.0
Boltz-1 |pandas |	BSD-3
Boltz-1 |MODEL WEIGHTS |	MIT