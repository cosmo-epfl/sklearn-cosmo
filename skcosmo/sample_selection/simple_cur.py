import numpy as np
import scipy

from ._greedy import GreedySelector
from ..utils import X_orthogonalizer, Y_sample_orthogonalizer


class CUR(GreedySelector):
    """Transformer that performs Greedy Feature Selection by choosing samples
    which maximize the magnitude of the left singular vectors, consistent with
    classic CUR matrix decomposition.

    Parameters
    ----------

    n_samples_to_select : int or float, default=None
        The number of samples to select. If `None`, half of the samples are
        selected. If integer, the parameter is the absolute number of samples
        to select. If float between 0 and 1, it is the fraction of samples to
        select.

    score_thresh_to_select : float, default=None
        Threshold for the score. If `None` selection will continue until the
        number or fraction given by n_samples_to_select is chosen. Otherwise
        will stop when the score falls below the threshold.

    iterative : boolean
                whether to orthogonalize after each selection, defaults to `true`

    k : int
        number of eigenvectors to compute the importance score with, defaults to 1

    tolerance: float
         threshold below which scores will be considered 0, defaults to 1E-12

    progress_bar: boolean, default=False
                  option to use `tqdm <https://tqdm.github.io/>`_
                  progress bar to monitor selections

    Attributes
    ----------

    n_samples_to_select : int
        The number of samples that were selected.

    X_selected_ : ndarray (n_samples_to_select, n_features)
                  The samples selected

    y_selected_ : ndarray (n_samples_to_select, n_properties)
                  The corresponding target values for the samples selected

    X_current : ndarray (n_samples, n_features)
                  The samples, orthogonalized by previously selected samples

    y_current : ndarray (n_samples, n_properties)
                The properties, if supplied, orthogonalized by a regression on
                the previously selected samples

    n_selected_ : int
                The number of samples that have been selected thus far

    report_progress : callable
                A wrapper to report the progress of the selector using a `tqdm` style
                progress bar

    score_threshold : float (optional)
                A score below which to stop selecting samples

    selected_idx_ : ndarray of integers
                    indices of the selected samples, with respect to the
                    original fitted matrix

    support_ : ndarray of shape (n_samples,), dtype=bool
        The mask of selected samples.

    """

    def __init__(
        self,
        n_samples_to_select=None,
        score_thresh_to_select=None,
        iterative=True,
        k=1,
        tolerance=1e-12,
        progress_bar=False,
    ):

        scoring = self.score
        self.k = k
        self.iterative = iterative

        super().__init__(
            scoring=scoring,
            n_samples_to_select=n_samples_to_select,
            progress_bar=progress_bar,
            score_thresh_to_select=tolerance,
        )

    def _init_greedy_search(self, X, y, n_to_select):
        """
        Initializes the search. Prepares an array to store the selected
        samples and computes their initial importance score.
        """

        self.X_current = X.copy()
        if y is not None:
            self.y_current = y.copy()
        else:
            self.y_current = None

        self.pi_ = self._compute_pi(self.X_current, self.y_current)

        super()._init_greedy_search(X, y, n_to_select)

    def _continue_greedy_search(self, X, y, n_to_select):
        """
        Continues the search. Prepares an array to store the selected
        samples, orthogonalizes the samples by those already selected,
        and computes their initial importance.
        """

        self.X_current = X_orthogonalizer(X.T, x2=self.X_selected_.T).T
        if self.y_current is not None:
            self.y_current = Y_sample_orthogonalizer(
                self.y_current,
                self.X_current,
                y_ref=self.y_selected_,
                X_ref=self.X_selected_,
                tol=1e-12,
            )
        self.pi_ = self._compute_pi(self.X_current, self.y_current)
        super()._continue_greedy_search(X, y, n_to_select)

    def score(self, X, y):
        """
        Returns the current importance of all samples
        """

        return self.pi_

    def _compute_pi(self, X, y=None):
        """
        For sample selection, the importance score :math:`\\pi` is the sum over
        the squares of the first :math:`k` components of the right singular vectors

        .. math::

            \\pi_j =
            \\sum_i^k \\left(\\mathbf{U}_\\mathbf{\\tilde{C}}\\right)_{ij}^2.

        where :math:`{\\mathbf{C} = \\mathbf{X}^T\\mathbf{X}.
        """

        U, _, _ = scipy.sparse.linalg.svds(
            X,
            k=self.k,
        )
        U = np.real(U)
        new_pi = (U[:, : self.k] ** 2.0).sum(axis=1)
        return new_pi

    def _update_post_selection(self, X, y, last_selected):
        """
        Saves the most recently selected sample, increments the sample counter,
        and, if the CUR is iterative, orthogonalizes the remaining samples by
        the most recently selected.
        """
        super()._update_post_selection(X, y, last_selected)

        if self.iterative:
            if self.y_current is not None:
                self.y_current = Y_sample_orthogonalizer(
                    self.y_current,
                    self.X_current,
                    y_ref=self.y_selected_,
                    X_ref=self.X_selected_,
                    tol=1e-12,
                )
            self.X_current = X_orthogonalizer(
                x1=self.X_current.T, c=last_selected, tol=1e-12
            ).T

            self.pi_ = self._compute_pi(self.X_current, self.y_current)

        self.pi_[last_selected] = 0.0
