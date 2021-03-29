import numpy as np
import scipy

from ._greedy import GreedySelector
from ..utils.orthogonalizers import X_orthogonalizer, Y_feature_orthogonalizer


class CUR(GreedySelector):
    """Transformer that performs Greedy Feature Selection using by choosing features
    which maximize the magnitude of the right singular vectors, consistent with
    classic CUR matrix decomposition.


    Parameters
    ----------

    n_features_to_select : int or float, default=None
        The number of features to select. If `None`, half of the features are
        selected. If integer, the parameter is the absolute number of features
        to select. If float between 0 and 1, it is the fraction of features to
        select.

    score_thresh_to_select : float, default=None
        Threshold for the score. If `None` selection will continue until the
        number or fraction given by n_features_to_select is chosen. Otherwise
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

    n_features_to_select : int
        The number of features that were selected.

    X_selected_ : ndarray (n_samples, n_features_to_select)
                  The features selected

    X_current : ndarray (n_samples, n_features)
                  The features, orthogonalized by previously selected features

    y_current : ndarray (n_samples, n_properties)
                The properties, if supplied, orthogonalized by a regression on
                the previously selected features

    eligible_ : ndarray of shape (n_features,), dtype=bool
        A mask of features eligible for selection

    n_selected_ : int
        The number of features that have been selected thus far

    report_progress : callable
        A wrapper to report the progress of the selector using a `tqdm` style
        progress bar

    score_threshold : float (optional)
        A score below which to stop selecting points

    selected_idx_ : ndarray of integers
                    indices of the selected features, with respect to the
                    original fitted matrix

    support_ : ndarray of shape (n_features,), dtype=bool
        The mask of selected features.

    """

    def __init__(
        self,
        n_features_to_select=None,
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
            n_features_to_select=n_features_to_select,
            progress_bar=progress_bar,
            score_thresh_to_select=tolerance,
        )

    def _init_greedy_search(self, X, y, n_to_select):
        """
        Initializes the search. Prepares an array to store the selected
        features and computes their initial importance score.
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
        features, orthogonalizes the features by those already selected,
        and computes their initial importance.
        """

        self.X_current = X_orthogonalizer(X, x2=self.X_selected_)
        if self.y_current is not None:
            self.y_current = Y_feature_orthogonalizer(
                self.y_current, X=self.X_selected_, tol=1e-12
            )
        self.pi_ = self._compute_pi(self.X_current, self.y_current)

        super()._continue_greedy_search(X, y, n_to_select)

    def score(self, X, y):
        """
        Returns the current importance of all features
        """

        return self.pi_

    def _compute_pi(self, X, y=None):
        """
        For feature selection, the importance score :math:`\\pi` is the sum over
        the squares of the first :math:`k` components of the right singular vectors

        .. math::

            \\pi_j =
            \\sum_i^k \\left(\\mathbf{U}_\\mathbf{\\tilde{C}}\\right)_{ij}^2.

        where :math:`{\\mathbf{C} = \\mathbf{X}^T\\mathbf{X}.
        """

        _, _, Vt = scipy.sparse.linalg.svds(
            X,
            k=self.k,
        )
        new_pi = (np.real(Vt) ** 2.0).sum(axis=0)
        return new_pi

    def _update_post_selection(self, X, y, last_selected):
        """
        Saves the most recently selected feature, increments the feature counter,
        and, if the CUR is iterative, orthogonalizes the remaining features by
        the most recently selected.
        """
        super()._update_post_selection(X, y, last_selected)

        if self.iterative:
            self.X_current = X_orthogonalizer(
                x1=self.X_current, c=last_selected, tol=1e-12
            )
            if self.y_current is not None:
                self.y_current = Y_feature_orthogonalizer(
                    self.y_current, X=self.X_selected_, tol=1e-12
                )

            self.pi_[self.eligible_] = self._compute_pi(
                self.X_current[:, self.eligible_], self.y_current
            )
