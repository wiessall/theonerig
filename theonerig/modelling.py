# AUTOGENERATED! DO NOT EDIT! File to edit: 03_modelling.ipynb (unless otherwise specified).

__all__ = ['sigmoid', 'gaussian', 'gaussian_2D', 'sum_of_gaussian', 'sum_of_2D_gaussian', 'fit_sigmoid',
           'fit_spatial_sta', 'fit_temporal_sta', 'sin_exponent', 'sinexp_gauss', 'sinexp_sigm', 'fit_chirp_am',
           'fit_chirp_freq_epoch', 'repetition_quality_index', 'onoff_transient_index']

# Cell
import math
import scipy as sp
import scipy.optimize
from scipy.interpolate import interp1d
import numpy as np
from functools import partial

# Cell
_default_sigmoid_p = (1,1,0,0)
def sigmoid(x, sigma, amp, x0, y0):
    """Sigmoid function
    params:
        - x: 1D numpy array at which to evaluate the points
        - sigma: steepness of the sigmoid
        - amp: amplitude of the sigmoid
        - x0: shift in x of the sigmoid
        - y0: shift in y of the sigmoid
    """
    return amp / (1.0 + np.exp(-sigma*(x-x0))) + y0

_default_gaussian_p = (1,1,0,0)
def gaussian(x, sigma, amp, x0, y0):
    """Gaussian function
    params:
        - x: 1D numpy array at which to evaluate the points
        - sigma: width of the gaussian
        - amp: amplitude of the gaussian
        - x0: shift in x of the gaussian
        - y0: shift in y of the gaussian
    """
    return amp * np.exp(-(x-x0)**2 / (2*sigma**2)) + y0

_default_2Dgaussian_p = (1,1,1,0,0,0,0)
def gaussian_2D(xz, sigma_x, sigma_z, amp, theta, x0, z0, y0):
    """Two dimensional Gaussian function
    params:
        - xz: meshgrid of x and z coordinates at which to evaluate the points
        - sigma_x: width of the gaussian
        - sigma_z: height of the gaussian
        - amp: amplitude of the gaussian
        - theta: angle of the gaussian (in radian)
        - x0: shift in x of the gaussian
        - z0: shift in z of the gaussian
        - y0: shift in y of the gaussian
    """
    (x,z) = xz
    x0, z0 = float(x0), float(z0)
    a =  (np.cos(theta)**2)/(2*sigma_x**2) + (np.sin(theta)**2)/(2*sigma_z**2)
    b = -(np.sin(2*theta)) /(4*sigma_x**2) + (np.sin(2*theta)) /(4*sigma_z**2)
    c =  (np.sin(theta)**2)/(2*sigma_x**2) + (np.cos(theta)**2)/(2*sigma_z**2)
    g = amp * np.exp( -(a*((x-x0)**2) + 2*b*(x-x0)*(z-z0) + c*((z-z0)**2))) + y0
    return g.ravel()

def sum_of_gaussian(t, sigma_1, amp_1, x0_1,
                       sigma_2, amp_2, x0_2, y0):
    """
    Sum of gaussian, using the gaussian function
    params:
        - t: 1D numpy array at which to evaluate the points
        - sigma_1: width of the 1st gaussian
        - amp_1: amplitude of the 1st gaussian
        - x0_1: shift in x of the 1st gaussian
        - sigma_2: width of the 2nd gaussian
        - amp_2: amplitude of the 2nd gaussian
        - x0_2: shift in x of the 2nd gaussian
        - y0: shift in y of the gaussian"""
    return (gaussian(t, sigma_1, amp_1, x0_1, 0)
            + gaussian(t, sigma_2, amp_2, x0_2, 0) + y0)

def sum_of_2D_gaussian(xz, sigma_x_1, sigma_z_1, amp_1, theta_1, x0_1, z0_1,
                           sigma_x_2, sigma_z_2, amp_2, theta_2, x0_2, z0_2, y0):
    return (gaussian_2D(xz, sigma_x_1, sigma_z_1, amp_1, theta_1, x0_1, z0_1, 0)
            + gaussian_2D(xz, sigma_x_2, sigma_z_2, amp_2, theta_2, x0_2, z0_2, 0) + y0)




# Cell
def fit_sigmoid(nonlin, t=None):
    if t is None:
        t = range(len(nonlin))
    bounds = ([0.000001, -np.inf     , -np.inf     , 0],
              [np.inf  , np.inf, np.inf, np.max(nonlin)])
    try:
        fit, _ = sp.optimize.curve_fit(sigmoid, t, nonlin, maxfev=10000, bounds=bounds)
        fit  = {"sigma":fit[0],"amp":fit[1],"x0":fit[2],"y0":fit[3]}
    except RuntimeError:
        fit = {"sigma":1,"amp":0,"x0":0,"y0":0}
    model = sigmoid(t, **fit)
    quality_index =  1 - (np.var(nonlin-model)/np.var(nonlin))
    return fit, quality_index

def fit_spatial_sta(sta):
    shape_y, shape_x = sta.shape
    eps = 0.000001
    argmax = np.unravel_index(sta.argmax(), sta.shape)
    argmin = np.unravel_index(sta.argmin(), sta.shape)
    #                   sigma_x    sigma_z   amp theta      x0        z0      y0
    bounds_center   = ((0,         0,         0,  0,         0,       0,       0),
                       (shape_x*4, shape_y*4, 2,  2*math.pi, shape_x, shape_y, eps))
    if sta[argmax] < abs(sta[argmin]):
        argmax, argmin  = argmin, argmax
        bounds_center   = ((0,         0,        -2,  0,         0,       0,       0),
                           (shape_x*4, shape_y*4, 0,  2*math.pi, shape_x, shape_y, eps))

    x    = np.arange(shape_x)
    z    = np.arange(shape_y)
    x, z = np.meshgrid(x, z)
    #                   sigma_x sigma_z  amp        theta      x0        z0       y0
    init_fit_center   = (  1,     1,    sta[argmax],  0,   argmax[1],  argmax[0], 0)
    data_tofit          = sta.reshape(-1)
    if np.isnan(sp.sum(sta)): #We check that the sta exists, otherwise return default zero model
        res  = {"sigma_x_1": 1, "sigma_z_1":1, "amp_1":0, "theta_1":0, "x0_1":0, "z0_1":0,
                "sigma_x_2": 1, "sigma_z_2":1, "amp_2":0, "theta_2":0, "x0_2":0, "z0_2":0, "y0":0}
    else:
        try:
            fit_c, _   = sp.optimize.curve_fit(gaussian_2D, (x,z), data_tofit, p0=init_fit_center, bounds=bounds_center)
            tmp_to_fit =  data_tofit - gaussian_2D((x,z), *fit_c)
            #                   sigma_x    sigma_z   amp theta        x0            z0           y0
            bounds_surround = ((0,         0,        -2,  0,         fit_c[4],     fit_c[5],     0),
                               (shape_x*4, shape_y*4, 0,  2*math.pi, fit_c[4]+eps, fit_c[5]+eps, eps))
            init_fit_surround = (  2,      2,         0,  0,         fit_c[4],     fit_c[5],     0)
            fit_s, _   = sp.optimize.curve_fit(gaussian_2D, (x,z), tmp_to_fit, p0=init_fit_surround, bounds=bounds_surround)

            init_fit_sum = (*fit_c[:-1],*fit_s[:-1],0)
            #Bounding only the position, that center fit should have found
            bounds_sum   = ((-np.inf,-np.inf,-np.inf,-np.inf,fit_c[4],fit_c[5],
                             -np.inf,-np.inf,-np.inf,-np.inf,fit_c[4],fit_c[5],-np.inf),
                            (np.inf, np.inf, np.inf, np.inf, fit_s[4]+eps,fit_s[5]+eps,
                             np.inf,np.inf,np.inf,np.inf,fit_s[4]+eps,fit_s[5]+eps,np.inf))
            fit_sum, _ = sp.optimize.curve_fit(sum_of_2D_gaussian, (x,z), data_tofit, p0=init_fit_sum, bounds=bounds_sum)
            fit  = {"sigma_x_1": fit_sum[0], "sigma_z_1":fit_sum[1], "amp_1":fit_sum[2],
                    "theta_1":fit_sum[3], "x0_1":fit_sum[4], "z0_1":fit_sum[5],
                    "sigma_x_2": fit_sum[6], "sigma_z_2":fit_sum[7], "amp_2":fit_sum[8],
                    "theta_2":fit_sum[9], "x0_2":fit_sum[10], "z0_2":fit_sum[11], "y0":fit_sum[12]}

        except RuntimeError: #If a model can't be fitted, we get a runtimeError
            fit  = {"sigma_x_1": 1, "sigma_z_1":1, "amp_1":0, "theta_1":0, "x0_1":0, "z0_1":0,
                    "sigma_x_2": 1, "sigma_z_2":1, "amp_2":0, "theta_2":0, "x0_2":0, "z0_2":0, "y0":0}
    model = sum_of_2D_gaussian((x,z), **fit)
    quality_index = 1 - (np.var(data_tofit-model)/np.var(data_tofit))
    return fit, quality_index


# Cell
def fit_temporal_sta(sta):
    argmax = sta.argmax()
    argmin = sta.argmin()
    if sta[argmax] < abs(sta[argmin]):
        argmax, argmin = argmin, argmax
    t = np.linspace((1-len(sta))/60, 0, len(sta))
    init_fit = (2, sta[argmin], (argmin-len(sta))/60, 2, sta[argmax], (argmax-len(sta))/60, 0)

                #sigma_1,   amp_1,  x0_1,      sigma_2,    amp_2,  x0_2,       y0
    bounds   = ((0,           -2, -len(sta)/60,        0,  -2,  -len(sta)/60,  -1),
                (len(sta)*4,  2,    1/60,     len(sta)*4,   2,     1/60,    1 ))

    if np.isnan(sp.sum(sta)): #We check that the sta exists, otherwise return default zero model
        res  = {"sigma_1":1,"amp_1":0,"x0_1":0,
                "sigma_2":1,"amp_2":0,"x0_2":0,"y0":0}
    else:
        try:
            fit, _ = sp.optimize.curve_fit(sum_of_gaussian, t, sta, p0=init_fit, bounds=bounds)

            fit  = {"sigma_1":fit[0],"amp_1":fit[1],"x0_1":fit[2],
                    "sigma_2":fit[3],"amp_2":fit[4],"x0_2":fit[5],"y0":fit[6]}
        except RuntimeError: #If a model can't be fitted, we get a runtimeError
            fit  = {"sigma_1":1,"amp_1":0,"x0_1":0,
                    "sigma_2":1,"amp_2":0,"x0_2":0,"y0":0}
    model = sum_of_gaussian(t, **fit)
    quality_index = 1 - (np.var(sta-model)/np.var(sta))
    return fit, quality_index

# Cell
def sin_exponent(x, amp, phi, freq, exp):
    """Sine raised to an exponent power. To the power 2, the sine is going between 0 and 1
    while its period is halfed. Subsequent round powers have the effect of narowing the peaks
    and making the rest of the sine approach zero. (graph it to see it)"""

    #Multiply by pi instead of 2pi because it expect the cos to be at least squared
    #Same goes for phi that I halfed so the period is still 2pi
    return np.power(np.sin((x*freq*np.pi)+(phi/2)), exp)*amp

def sinexp_gauss(x, sigma, x0, amp, phi, freq, exp):
    return sin_exponent(x, amp, phi, freq, exp) * gaussian(x, sigma, 1, x0, 0)

def sinexp_sigm(x, sigma, x0, y0, amp, phi, freq, exp):
    return sin_exponent(x, amp, phi, freq, exp) * sigmoid(x, sigma, 1, x0, 0) + y0

def fit_chirp_am(cell_mean, start=420, stop=960, freq=1.5):
    """Fit a sinexp_sigm to the mean response of a cell to chirp_am.
    return :
        - fit, or None if fit not found
        - quality index (explained variance)"""

    to_fit = np.convolve([1/5]*5,cell_mean, mode="same")[start:stop]  #Smoothing
    t = np.linspace(0, len(to_fit)/60, len(to_fit), endpoint=False)

    #If suppressed by contrast cell, the firing should be higher in first part of chirp
    fit_positive = np.mean(to_fit[:len(to_fit)//2]) < np.mean(to_fit[len(to_fit)//2:])

    #The iterations fit different exponent/gaussian, and the first in addition fit phi.
    try:
        sinexp_part = partial(sin_exponent, freq=freq, exp=2)
        fit, _ = sp.optimize.curve_fit(sinexp_part, t, to_fit,
                                         bounds=[( 0            , 0),
                                                 (np.max(to_fit), 2*np.pi)],
                                            p0 = (np.max(to_fit), 0))

        best_fit = (50, 0, 0, *fit, freq, 2)
        tmp_diff = np.sum(np.square(sinexp_sigm(t, *best_fit) - to_fit))
        phi = fit[1]
    except:
        best_fit = (1, 0, 0, 0, 0, freq, 0)
        tmp_diff = np.inf

    for exp in np.exp2(range(1,10)): #Fitting the data with different sin exponents, to narrow the fit
        try:
            sinexp_sigm_part = partial(sinexp_sigm, freq=freq, exp=exp)
            if fit_positive:
                fit, _ = sp.optimize.curve_fit(sinexp_sigm_part, t, to_fit,
                                               bounds=[(  0,    0          ,        0       ,      0        , 0),
                                                        (50, len(to_fit)/60,  np.max(to_fit), np.max(to_fit), 2*np.pi)],
                                               p0 =      (1, len(to_fit)/120,       0       , np.max(to_fit), phi))
            else:
                fit, _ = sp.optimize.curve_fit(sinexp_sigm_part, t, to_fit,
                                               bounds=[(  0,    0          ,        0       ,-np.max(to_fit), 0),
                                                        (50, len(to_fit)/60,  np.max(to_fit),     0         , 2*np.pi)],
                                               p0 =     (1, len(to_fit)/120,  np.max(to_fit) ,-np.max(to_fit),(phi+np.pi)%(2*np.pi)))

            mse = np.sum(np.square(sinexp_sigm_part(t, *fit) - to_fit))
            if mse < tmp_diff:
                best_fit = (*fit, freq, exp)
                tmp_diff = mse
        except:
            continue
    best_fit = dict((k, v) for v, k in zip(best_fit, ["sigma","x0","y0","amp","phi","freq","exp"]))

    model = sinexp_sigm(t, **best_fit)
    quality_index = 1 - (np.var(to_fit-model)/np.var(to_fit))
    return best_fit, quality_index

def fit_chirp_freq_epoch(cell_mean, freqs=[1.875,3.75,7.5,15,30], durations=[2,2,2,1,1]):
    """Takes the mean response of a cell to chirp_freq_epoch and fit a sine_exponent to
    each frequency.
    return :
        - list of five fit (1 per freq, None if fit not found)
        - list of five quality index (explained variance)"""
    best_fit_l = []
    qualityidx_l = []

    cursor = 360 #Start of the freqs

    #We fit each freqency epoch with a cos function
    for freq, dur in zip(freqs, durations):
        n_rep, n_fr = int(dur*freq), int(60/freq)
        edgecut = 10
        cursor += edgecut
        len_fit = n_rep*n_fr - edgecut

        #Upsampling of the data to prevent low sampling effects with high freq sine
        upsamp = 10
        to_fit = cell_mean[cursor:cursor+len_fit+1]
        t = np.linspace(0, len_fit/60, len_fit*upsamp, endpoint=False)
        to_fit = interp1d(np.linspace(0,len(to_fit)/60, len(to_fit), endpoint=False), to_fit)(t)

        best_fit = None
        tmp_diff = np.inf
        for exp in np.exp2(range(1,10)): #Fitting the data with different cos exponents, to narrow the fit
            try:
                sin_exponent_part = partial(sin_exponent, freq=freq, exp=exp)
                fit, cov = sp.optimize.curve_fit(sin_exponent_part, t, to_fit, bounds=[(0,          0),
                                                                                       (max(to_fit),np.pi*2)])
                mse = np.sum(np.square(sin_exponent_part(t, *fit) - to_fit))
                if mse < tmp_diff:
                    best_cov = cov
                    best_fit = (*fit, freq, exp)
                    tmp_diff = mse
            except:
                continue
        if best_fit is not None:
            best_fit = dict((k, v) for v, k in zip(best_fit, ["amp","phi","freq","exp"]))
            best_fit_l.append(best_fit)
            model = sin_exponent(t, **best_fit)
            qualityidx_l.append(1 - (np.var(to_fit-model)/np.var(to_fit)))
        else:
            best_fit_l.append({"amp":0,"phi":0,"freq":freq,"exp":0})
            qualityidx_l.append(0)

        cursor += len_fit
    return best_fit_l, qualityidx_l #, best_cov_l

# Cell
def repetition_quality_index(cell_response):
    """Return a quality index of cell response to a repeated stimulus.
    params:
        - cell_response: response of a cell of shape (n_rep, time)"""
    tmp1 = np.var(np.mean(cell_response, axis=0)) #VAR(MEAN(C)repeat)time
    tmp2 = np.mean(np.var(cell_response, axis=1)) #MEAN(VAR(C)time)repeat
    quality = tmp1/tmp2
    return quality

def onoff_transient_index(cell_response, start_on=120, stop_on=240, start_off=240, stop_off=360):
    """Return both on-off and transient indexes of cell response.
    params:
        - cell_response: response of a cell of shape (time,...)
        - start_on:  starting index of ON stimulation
        - stop_on:   stop index of ON stimulation
        - start_off: starting index of OFF stimulation
        - stop_off:  stop index of OFF stimulation"""
    #ON-OFF index
    on_response   = cell_response[start_on:stop_on]
    on_sum        = np.sum(on_response)
    off_response  = cell_response[start_off:stop_off]
    off_sum       = np.sum(off_response)
    onoff_indexes = (on_sum-off_sum)/(on_sum+off_sum)

    #Transient index
    if onoff_indexes>0: #Main ON response
        transient_sum   = np.sum(cell_response[start_on:start_on+30])
        sustained_sum   = np.sum(cell_response[start_on:stop_on])
    else:
        transient_sum   = np.sum(cell_response[start_off:start_off+30])
        sustained_sum   = np.sum(cell_response[start_off:stop_off])
    transient_index = transient_sum/sustained_sum

    return onoff_indexes, transient_index