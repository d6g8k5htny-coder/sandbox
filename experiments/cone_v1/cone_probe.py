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



def self_check(tol_se=8.0):
    """Bounded private sanity only. Not enclosure, not discharge, not review.
    Requires |mean-reference| <= tol_se * sample_standard_error on the fixed seed.
    """
    out = run()
    if out['certified'] is not False:
        raise AssertionError('certified must remain false')
    if out['role'] != 'exploratory sanity check only':
        raise AssertionError('role drift')
    gap = abs(out['mean'] - out['reference'])
    budget = tol_se * out['sample_standard_error']
    if gap > budget:
        raise AssertionError(f'exploratory gap {gap} exceeds {budget}')
    return {'ok': True, 'gap': gap, 'budget': budget, 'certified': False}


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--self-check':
        print(json.dumps(self_check(), indent=2, sort_keys=True))
    else:
        print(json.dumps(run(), indent=2, sort_keys=True))
