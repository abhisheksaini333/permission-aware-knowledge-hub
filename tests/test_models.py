import numpy as np
import pytest
from knowledge.models import mean_pool

def test_masked_pooling_ignores_padding_and_normalizes():
 out=mean_pool(np.array([[[1.,0],[0,1],[99,99]]]),np.array([[1,1,0]]))
 assert np.allclose(out,[[2**-.5,2**-.5]])
 assert np.allclose(mean_pool(np.zeros((1,2,2)),np.array([[0,0]])),[[0,0]])
