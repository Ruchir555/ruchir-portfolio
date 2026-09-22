"""Rebuild portfolio illustrations from reviewed public source checkouts.

Usage: python generate_visuals.py SOURCE_ROOT
SOURCE_ROOT contains repository-named folders, plus majorization.ipynb from
State-Transfer-between-CV-Bosonic-Modes-and-Qubits/T_parameter_finder.ipynb.
Requires numpy, scipy, matplotlib. No hardware or quantum-chemistry runs.
"""
from pathlib import Path
import ast
import json
import sys
import importlib.util
import runpy
import contextlib
import io
from types import SimpleNamespace as NS
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(sys.argv[1])
OUT = Path(__file__).resolve().parent
OUT.mkdir(exist_ok=True)
NAVY, LIME, CYAN, WHITE, MUTED = '#101d32', '#bcf277', '#70d7ee', '#edf3fa', '#aebdd1'
plt.rcParams.update({'figure.facecolor': NAVY, 'axes.facecolor': NAVY,
 'text.color': WHITE, 'axes.labelcolor': MUTED, 'xtick.color': MUTED,
 'ytick.color': MUTED, 'axes.edgecolor': '#43536a', 'font.size': 12,
 'svg.fonttype': 'none', 'font.family': 'DejaVu Sans'})
results = {}

def canvas(title, subtitle):
    fig, ax = plt.subplots(figsize=(8,4.8))
    fig.subplots_adjust(left=.13,right=.95,bottom=.19,top=.75)
    fig.text(.07,.91,title,fontsize=21,weight='bold')
    fig.text(.07,.83,subtitle,fontsize=11,color=MUTED)
    ax.spines[['top','right']].set_visible(False)
    return fig, ax

def save(fig,name):
    fig.savefig(OUT/f'{name}.svg',metadata={'Date':None})
    fig.savefig(OUT/f'{name}-preview.png',dpi=120)
    plt.close(fig)

def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

# Run the original Bloch dynamics, with a step-aligned pulse schedule.
m=module(ROOT/'dynamical-decoupling-sim/src/bloch_sim.py','bloch')
fig,ax=canvas('Refocusing a qubit','Free evolution and Hahn echo · original simulation routine')
for label,pulses,col in [('Free',[],CYAN),('Hahn echo',[5.0],LIME)]:
    t,b=m.simulate_sequence(10,.01,3,.12,pulses)
    ax.plot(t,b[:,0],color=col,lw=2,label=label)
    assert np.allclose(np.linalg.norm(b[:,:2],axis=1),np.exp(-.12*t),atol=1e-10)
    results[label+' final x']=float(b[-1,0])
ax.plot(t,np.exp(-.12*t),':',color=MUTED,lw=1.2,label='Decay envelope')
ax.axvline(5,color=LIME,lw=.8,alpha=.4)
ax.set(xlabel='Time (model units)',ylabel='Bloch component x',ylim=(-1.08,1.08))
fig.legend(loc='lower center',bbox_to_anchor=(.5,.005),ncol=3,frameon=False,fontsize=10)
save(fig,'dephasing')

# Execute the original integration script; restyle its returned convergence data.
with contextlib.redirect_stdout(io.StringIO()):
    d=runpy.run_path(str(ROOT/'Computational-Physics/integration_methods.py'))
plt.close('all')
fig,ax=canvas('Convergence, made visible','Gaussian quadrature · values from the original integration script')
ax.plot(d['index'],d['error_ydata'],color=LIME,lw=2.5,marker='.',ms=5)
ax.axhline(np.sqrt(np.pi),color=CYAN,ls='--',label=r'Analytical limit $\sqrt{\pi}$')
ax.set(xlabel='Number of sample points',ylabel='Integral estimate',xlim=(2,51))
ax.legend(frameon=False,loc='upper right',fontsize=11)
results['integration_error_vs_quad']=float(d['error'])
save(fig,'integration')

# Execute reviewed function definitions from notebook cells 2-5 only.
nb=json.loads((ROOT/'majorization.ipynb').read_text())
env={}
for i in [2,3,4,5]:
    tree=ast.parse(''.join(nb['cells'][i]['source']))
    funcs=ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[])
    exec(compile(funcs,'original-notebook-functions','exec'),env)
ts,ks=env['t_parameters']([5,3,2],[6,3,1],checkMajorization=True)
vec=np.array([6.,3.,1.]); states=[vec.copy()]
for i,(t,k) in enumerate(zip(ts,ks)):
    j=i+k-1; a,b=vec[i],vec[j]
    vec[i]=t*a+(1-t)*b;vec[j]=(1-t)*a+t*b;states.append(vec.copy())
assert np.allclose(vec,[5,3,2]) and all(np.isclose(v.sum(),10) for v in states)
fig,ax=canvas('Mixing toward a target','Two T-transformations · executed notebook example, normalised')
x=np.arange(3)
for i,(v,col) in enumerate(zip(states,[CYAN,'#b09af8',LIME])):
    ax.bar(x+(i-1)*.23,v/10,width=.21,color=col,label=['Initial','Step 1','Target'][i])
ax.set(xticks=x,xticklabels=['1','2','3'],xlabel='Vector component',ylabel='Normalised weight',ylim=(0,.7))
ax.legend(frameon=False,ncol=3,fontsize=11)
results['majorization']={'t':ts,'k':ks,'states':[v.tolist() for v in states]}
save(fig,'majorization')

# Original Traxis fitter, using marker-shaped objects instead of a Qt GUI.
m=module(ROOT/'Traxis_HEP_Capstone/traxis-1.0.2/traxis/calc/circlefit.py','circlefit')
rng=np.random.default_rng(17);theta=np.linspace(.18,2.65,30)
x=2+4*np.cos(theta)+rng.normal(0,.045,30)
y=-1+4*np.sin(theta)+rng.normal(0,.045,30)
def marker(x,y):
    center=NS(x=lambda:x,y=lambda:y)
    return NS(ellipse=NS(rect=lambda:NS(center=lambda:center)))
markers=[marker(a,b) for a,b in zip(x,y)]
fit=m.fitCircle(NS(count=lambda:len(markers),item=lambda i:markers[i]))
assert abs(fit['radius']-4)<.1
fig,ax=canvas('Reconstructing a particle track','Synthetic markers · original Traxis least-squares circle fit')
ang=np.linspace(.12,2.75,200)
ax.plot(fit['centerX']+fit['radius']*np.cos(ang),fit['centerY']+fit['radius']*np.sin(ang),color=LIME,lw=2.5,label='Fitted arc')
ax.scatter(x,y,s=25,facecolors=NAVY,edgecolors=CYAN,zorder=3,label='Synthetic points')
ax.set(xlabel='x (arbitrary units)',ylabel='y (arbitrary units)');ax.set_aspect('equal')
ax.legend(frameon=False,fontsize=10,loc='lower center')
results['traxis_fit']={k:float(v) for k,v in fit.items()}
save(fig,'traxis')

# Explanatory drawing grounded in the two firmware files, not a hardware run.
fig,ax=canvas('Sensing meets control','AER201 team project · architecture reconstructed from firmware')
ax.set(xlim=(0,10),ylim=(0,5));ax.axis('off')
def box(x,y,w,h,text,col):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.12',facecolor='#1b2e46',edgecolor=col,lw=1.4))
    ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=12,color=WHITE)
def arrow(a,b):
    ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','color':MUTED,'lw':1.5})
box(.1,3.1,3,1.3,'Ultrasonic / IR\nBreak-beam sensors',CYAN)
box(.1,.3,3,1.3,'Arduino Nano\nSensor acquisition',CYAN)
box(5,.3,4,1.3,'PIC18F4620\nRobot control',LIME)
box(5,3.1,4,1.3,'Motors / actuators\nKeypad + LCD',LIME)
arrow((1.6,3),(1.6,1.75));arrow((3.25,.95),(4.85,.95));arrow((7,1.75),(7,3))
ax.text(4.05,1.45,'I²C',ha='center',color=MUTED)
save(fig,'robotics')

# New illustration of fixed-endpoint variations in the Lagrangian notes.
fig,ax=canvas('Different paths. Shared endpoints.','Hamilton’s principle · explanatory illustration of the notes')
t=np.linspace(0,1,200);base=.2+.6*t
for eps in [-.25,-.12,.12,.25]:
    ax.plot(t,base+eps*np.sin(np.pi*t),color=CYAN,alpha=.55,lw=1.5)
ax.plot(t,base,color=LIME,lw=3,label='Stationary path: free-particle example')
ax.scatter([0,1],[.2,.8],color=LIME,zorder=5,s=45)
ax.set(xlabel='Time',ylabel='Generalised coordinate',xticks=[0,1],xticklabels=['Initial','Final'],yticks=[])
ax.text(.45,.25,r'$\delta S = 0$',fontsize=25,color=LIME)
ax.legend(frameon=False,loc='upper left',fontsize=10)
save(fig,'notes')

# Recompute the report's analytic nearest-neighbour dispersion, not its DFT.
fig=plt.figure(figsize=(8,4.8),facecolor=NAVY)
fig.text(.07,.91,'Where graphene’s bands meet',fontsize=21,weight='bold',color=WHITE)
fig.text(.07,.83,'Tight-binding illustration · t′ = 0 · recreated from the report equation',fontsize=11,color=MUTED)
ax=fig.add_axes([.13,.08,.75,.70],projection='3d',facecolor=NAVY)
kx,ky=np.meshgrid(np.linspace(-.65,.65,55),np.linspace(4*np.pi/(3*np.sqrt(3))-.65,4*np.pi/(3*np.sqrt(3))+.65,55))
f=2*np.cos(np.sqrt(3)*ky)+4*np.cos(np.sqrt(3)/2*ky)*np.cos(1.5*kx)
e=np.sqrt(np.maximum(0,3+f))
ax.plot_surface(kx,ky,e,color=LIME,alpha=.85,linewidth=0,rstride=2,cstride=2)
ax.plot_surface(kx,ky,-e,color=CYAN,alpha=.85,linewidth=0,rstride=2,cstride=2)
ax.set(xlabel='kₓa',ylabel='kᵧa',zlabel='E / t');ax.view_init(elev=18,azim=-50)
ax.xaxis.pane.fill=ax.yaxis.pane.fill=ax.zaxis.pane.fill=False
ax.grid(False);ax.tick_params(labelsize=8)
save(fig,'graphene')
(OUT/'verification.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
