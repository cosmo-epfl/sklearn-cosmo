---
title: 'scikit-COSMO: A Toolbox of Machine Learning Methods for Materials Science'
tags:
    - Python
authors:
    - name: Rose K. Cersonsky ^ [\url{mailto: rose.cersonsky@epfl.ch}]
    orcid: 0000-0003-4515-3441
    affiliation: 1
    - name: Guillaume Fraux
    orcid: 0000-0003-4824-6512
    affiliation: 1
    - name: Sergei Kliavinek
    orcid: 0000-0001-8326-325X
    affiliation: 1
    - name: Alexander Goscinski
    orcid: 0000-0001-8076-215X
    affiliation: 1
    - name: Benjamin A. Helfrecht
    orcid: 0000-0002-2260-7183
    affiliation: 1
    - name: Michele Ceriotti ^ [\url{mailto: michele.ceriotti@epfl.ch}]
    orcid: 0000-0003-2571-2832
    affiliation: 1
affiliations:
    - name: Laboratory of Computational Science and Modeling(COSMO), École Polytechnique Fédérale de Lausanne(EPFL), Lausanne, Switzerland
    index: 1
date: 03 May 2021
bibliography: paper.bib
---

# Summary

`scikit-COSMO` (skcosmo) focuses on machine learning methods that are of particular use (but not limited to) the field of materials science and computational chemistry. Currently, many
machine learning studies employ the foundational `scikit-learn` repository, a
collection of widely applicable machine learning algorithms and methods.
Written in the same language (Python), style, and with guidelines, we aim to provide
users the ability to seamlessly include methods tailored for material science in machine learning
workflows alongside those from `scikit-learn`.

# Statement of need

The `scikit-COSMO` package provides machine learning algorithms developed for a specific
community: those who use machine learning to understand or represent collections
of atoms or molecules. The emphasis put upon each subclass of machine learning
algorithms varies within different subfields. For example, in applying machine
learning to collections of atoms, there is a necessary focus on the
representation of data in a numerical format for machine learning pipelines,
known as _featurization_. Many machine learning studies represent samples using
real-world measurements or tests, effectively limiting the number of features
based upon the resources available. When representing a collection of atoms,
there is both a variety of featurization techniques to employ and a wealth of
tunable hyperparameters within each technique. Thus, the size of the vectors
which represent atoms is almost unbounded, and it becomes necessary to assess
their utility, remove redundancies, or condense them. Currently, `scikit-COSMO`
contains algorithms to address these specific problems, all of which were
previously-unavailable within open-source repositories.

- Feature Reconstruction Measures[@Goscinski2021] - both global and local measures
of the information density for a given representation. This set of
unsupervised algorithms is of particular use in the choice of representation
and hyperparameter optimization.
- Feature and Sample Selection[@Imbalzano2018
                               @Cersonsky2021] - methods focused on determining
a diverse or information-rich subset of features or samples for machine
learning problems.
- Hybrid Supervised-Unsupervised Dimensionality Reduction and Regression[@deJong1992
                                                @Helfrecht2020] - linear and
non-linear techniques to combine features into latent-space projections
(similar to PCA) that also incorporate target information. This is of particular
use when condensing features prior to property regression or constructing
structure-property maps, such as those analyzable via[@Fraux2020].

`scikit-COSMO` itself does not compute atomic descriptors directly, and instead takes as input descriptors computed by other software such as `librascal` [@Musil2021],
QUIP[@quip], and `DScribe`[https://github.com/SINGROUP/dscribe].

scikit-COSMO also contains minimal datasets used to test the implementation, including a small
subset of molecules and their NMR chemical shieldings, as reported in [@Ceriotti2019].

# Acknowledgements

We acknowledge contributions from the entire COSMO team, particularly
Giulio Imbalzano and Max Veit.

# References
