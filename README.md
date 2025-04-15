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
Please see LICENSE for the details of the license. Some packages, tools, and code used inside individual tutorials are under their own licenses as described therein. Please ensure you read the details of the tutorials and licensing of individual tools.