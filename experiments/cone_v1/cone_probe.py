"""Private exploratory cone probe. Not an interval enclosure or proof.
Only synthetic Gaussian draws. No credentials, Drive data or network operations.
"""
import json
import math
import random


def run(samples=200000,seed=20260924):
    if type(samples) is not int or not 2<=samples<=2000000:
        raise ValueError('sample count outside bounded experiment')
    rng=random.Random(seed)
    total=squares=0.0
    for _ in range(samples):
        s=rng.gauss(0,math.sqrt(5/3))
        x=rng.gauss(0,1); y=rng.gauss(0,1)
        r2=x*x+y*y
        value=(s*s-r2)**2 if s<0 and s*s>r2 else 0.0
        total+=value; squares+=value*value
    mean=total/samples
    se=math.sqrt(max(0,(squares-samples*mean*mean)/(samples-1))/samples)
    return {'samples':samples,'seed':seed,'mean':mean,'sample_standard_error':se,
            'reference':29/6-math.sqrt(6),'incorrect_untruncated_half_moment':29/6,
            'role':'exploratory sanity check only','certified':False}


if __name__=='__main__':
    print(json.dumps(run(),indent=2,sort_keys=True))
