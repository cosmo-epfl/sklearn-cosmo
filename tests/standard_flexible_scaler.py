import unittest
from skcosmo.preprocessing.flexible_scaler import StandardFlexibleScaler
from sklearn.preprocessing import StandardScaler
import sklearn
import numpy as np


class ScalerTests(unittest.TestCase):
    def test_fit_transform_pf(self):
        """Checks that in the case of normalization by columns,
        the result is the same as in the case of using the package from sklearn
        """
        X = np.random.uniform(0, 100, size=(3, 3))
        model = StandardFlexibleScaler(column_wise=True)
        transformed_skcosmo = model.fit_transform(X)
        transformed_sklearn = StandardScaler().fit_transform(X)
        self.assertTrue(
            (np.isclose(transformed_sklearn, transformed_skcosmo, atol=1e-12)).all()
        )

    def test_fit_transform_npf(self):
        """Checks that the entire matrix is correctly normalized
        (not column-wise). Compare with the value calculated
        directly from the equation.
        """
        X = np.random.uniform(0, 100, size=(3, 3))
        model = StandardFlexibleScaler(column_wise=False)
        X_tr = model.fit_transform(X)
        mean = X.mean(axis=0)
        var = ((X - mean) ** 2).mean(axis=0)
        scale = np.sqrt(var.sum())
        X_ex = (X - mean) / scale
        self.assertTrue((np.isclose(X_ex, X_tr, atol=1e-12)).all())

    def test_transform(self):
        """Checks the transformation relative
        to the reference matrix.
        """
        X = np.random.uniform(0, 100, size=(3, 3))
        model = StandardFlexibleScaler(column_wise=True)
        model.fit(X)
        Y = np.random.uniform(0, 100, size=(3, 3))
        Y_tr = model.transform(Y)
        mean = X.mean(axis=0)
        var = ((X - mean) ** 2).mean(axis=0)
        scale = np.sqrt(var)
        Y_ex = (Y - mean) / scale
        self.assertTrue((np.isclose(Y_tr, Y_ex, atol=1e-12)).all())

    def test_inverse_transform(self):
        """Checks the inverse transformation with
        respect to the reference matrix.
        """
        X = np.random.uniform(0, 100, size=(3, 3))
        model = StandardFlexibleScaler(column_wise=True)
        model.fit(X)
        Y = np.random.uniform(0, 100, size=(3, 3))
        Y_tr = model.transform(Y)
        Y = np.around(Y, decimals=4)
        Y_inv = np.around((model.inverse_transform(Y_tr)), decimals=4)
        self.assertTrue((np.isclose(Y, Y_inv, atol=1e-12)).all())
        X = np.random.uniform(0, 100, size=(3, 3))
        model = StandardFlexibleScaler(column_wise=False)
        model.fit(X)
        Y = np.random.uniform(0, 100, size=(3, 3))
        Y_tr = model.transform(Y)
        Y = np.around(Y, decimals=4)
        Y_inv = np.around((model.inverse_transform(Y_tr)), decimals=4)
        self.assertTrue((np.isclose(Y, Y_inv, atol=1e-12)).all())

    def test_NotFittedError_transform(self):
        """Checks that an error is returned when
        trying to use the transform function
        before the fit function"""
        X = np.random.uniform(0, 100, size=(3, 3))
        model = StandardFlexibleScaler(column_wise=True)
        with self.assertRaises(sklearn.exceptions.NotFittedError):
            model.transform(X)

    def test_shape_inconsistent_transform(self):
        """Checks that an error is returned when attempting
        to use the transform function with mismatched matrix sizes."""
        X = np.random.uniform(0, 100, size=(3, 3))
        X_test = np.random.uniform(0, 100, size=(4, 4))
        model = StandardFlexibleScaler(column_wise=True)
        model.fit(X)
        with self.assertRaises(ValueError):
            model.transform(X_test)

    def test_shape_inconsistent_inverse(self):
        """Checks that an error is returned when attempting
        to use the inverse transform function with mismatched matrix sizes."""
        X = np.random.uniform(0, 100, size=(3, 3))
        X_test = np.random.uniform(0, 100, size=(4, 4))
        model = StandardFlexibleScaler(column_wise=True)
        model.fit(X)
        with self.assertRaises(ValueError):
            model.inverse_transform(X_test)

    def test_NotFittedError_inverse(self):
        """Checks that an error is returned when
        trying to use the inverse transform function
        before the fit function"""
        X = np.random.uniform(0, 100, size=(3, 3))
        model = StandardFlexibleScaler()
        with self.assertRaises(sklearn.exceptions.NotFittedError):
            model.inverse_transform(X)

    def test_ValueError_column_wise(self):
        """Checks that the matrix cannot be normalized
        across columns if there is a zero variation column."""
        X = np.random.uniform(0, 100, size=(3, 3))
        X[0][0] = X[1][0] = X[2][0] = 2
        model = StandardFlexibleScaler(column_wise=True)
        with self.assertRaises(ValueError):
            model.fit(X)

    def test_ValueError_full(self):
        """Checks that the matrix cannot be normalized
        if there is a zero variation matrix."""
        X = np.array([2, 2, 2]).reshape(-1, 1)
        model = StandardFlexibleScaler(column_wise=False)
        with self.assertRaises(ValueError):
            model.fit(X)


if __name__ == "__main__":
    unittest.main()
