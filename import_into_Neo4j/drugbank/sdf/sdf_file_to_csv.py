import sys


from rdkit import Chem

##################################################################################################################
'''
Extract from rdkit.Chem.PandasTools but a little bit modified
'''
try:
  import pandas as pd


  if 'display.width' in pd.core.config._registered_options:
    pd.set_option('display.width', 1000000000)
  if 'display.max_rows' in pd.core.config._registered_options:
    pd.set_option('display.max_rows', 1000000000)
  elif 'display.height' in pd.core.config._registered_options:
    pd.set_option('display.height', 1000000000)
  if 'display.max_colwidth' in pd.core.config._registered_options:
    pd.set_option('display.max_colwidth', 1000000000)
  # saves the default pandas rendering to allow restauration
  defPandasRendering = pd.core.frame.DataFrame.to_html
except Exception as e:
  pd = None

try:
  from rdkit.Avalon import pyAvalonTools as pyAvalonTools
  _fingerprinter=lambda x,y:pyAvalonTools.GetAvalonFP(x,isQuery=y,bitFlags=pyAvalonTools.avalonSSSBits)


except ImportError:
  _fingerprinter=lambda x,y:Chem.PatternFingerprint(x,fpSize=2048)

def _MolPlusFingerprint(m):
  '''Precomputes fingerprints and stores results in molecule objects to accelerate substructure matching
  '''
  #m = Chem.MolFromSmiles(smi)
  if m is not None:
    m._substructfp=_fingerprinter(m,False)
  return m

def patchPandasHTMLrepr(self,**kwargs):
  '''
  Patched default escaping of HTML control characters to allow molecule image rendering dataframes
  '''
  formatter = pd.core.format.DataFrameFormatter(self,buf=None,columns=None,col_space=None,colSpace=None,header=True,index=True,
                                               na_rep='NaN',formatters=None,float_format=None,sparsify=None,index_names=True,
                                               justify = None, force_unicode=None,bold_rows=True,classes=None,escape=False)
  formatter.to_html()
  html = formatter.buf.getvalue()
  return html

def RenderImagesInAllDataFrames(images=True):
  '''Changes the default dataframe rendering to not escape HTML characters, thus allowing rendered images in all dataframes.
  IMPORTANT: THIS IS A GLOBAL CHANGE THAT WILL AFFECT TO COMPLETE PYTHON SESSION. If you want to change the rendering only
  for a single dataframe use the "ChangeMoleculeRendering" method instead.
  '''
  if images:
    pd.core.frame.DataFrame.to_html = patchPandasHTMLrepr
  else:
    pd.core.frame.DataFrame.to_html = defPandasRendering

def LoadSDF(filename, idName='ID',molColName = 'ROMol',includeFingerprints=False, isomericSmiles=False, smilesName=None):
  """ Read file in SDF format and return as Pandas data frame """
  df = None
  if type(filename) is str:
    f = open(filename, 'rb') #'rU')
  else:
    f = filename
  for i, mol in enumerate(Chem.ForwardSDMolSupplier(f)):
    if i==3872 :
      print('blub')
    if mol is None: continue
    row = dict((k, mol.GetProp(k)) for k in mol.GetPropNames())
    # if row['DATABASE_ID']=='DB00225':
    #   print('drinne')
    #   sys.exit()
    if i==3872 :
      print(row)
    if mol.HasProp('_Name'): row[idName] = mol.GetProp('_Name')
    if smilesName is not None:
      row[smilesName] = Chem.MolToSmiles(mol, isomericSmiles=isomericSmiles)
    if not includeFingerprints:
        row[molColName] = mol
    else:
        row[molColName] = _MolPlusFingerprint(mol)
    row = pd.DataFrame(row, index=[i])
    if df is None:
      df = row
    else:
      df = df.append(row)
  f.close()
  RenderImagesInAllDataFrames(images=True)
  return df

#####################################################################################################################

if len(sys.argv)!=3:
  sys.exit('This need as input a sdf file and an output file name as .csv')
my_sdf_file = sys.argv[1]
to_file=sys.argv[2]


frame = LoadSDF(my_sdf_file,
                            smilesName='SMILES',
                            molColName='Molecule',
                            includeFingerprints=False)

frame.to_csv(to_file)

####functioniert, aber schmeisst auch einige fehler
'''
hier sin 8 stueck weg gelassen worden bei metabolite-struture
[09:45:16]  S group SUP ignored on line 68719
[09:45:19] Explicit valence for atom # 40 N, 4, is greater than permitted
[09:45:19] ERROR: Could not sanitize molecule ending on line 133808
[09:45:19] ERROR: Explicit valence for atom # 40 N, 4, is greater than permitted
[09:45:19] Explicit valence for atom # 5 N, 4, is greater than permitted
[09:45:19] ERROR: Could not sanitize molecule ending on line 147504
[09:45:19] ERROR: Explicit valence for atom # 5 N, 4, is greater than permitted
[09:45:20]  S group SUP ignored on line 169420
[09:45:20]  S group SUP ignored on line 169736
[09:45:21] Explicit valence for atom # 38 O, 3, is greater than permitted
[09:45:21] ERROR: Could not sanitize molecule ending on line 183356
[09:45:21] ERROR: Explicit valence for atom # 38 O, 3, is greater than permitted
[09:45:21]  S group SUP ignored on line 185872
[09:45:21]  S group SUP ignored on line 186070
[09:45:21]  S group SUP ignored on line 186849
[09:45:21]  S group SUP ignored on line 187018
[09:45:21]  S group SUP ignored on line 187187
[09:45:21] Explicit valence for atom # 2 N, 4, is greater than permitted
[09:45:21] ERROR: Could not sanitize molecule ending on line 192374
[09:45:21] ERROR: Explicit valence for atom # 2 N, 4, is greater than permitted
[09:45:21] Explicit valence for atom # 2 N, 4, is greater than permitted
[09:45:21] ERROR: Could not sanitize molecule ending on line 192539
[09:45:21] ERROR: Explicit valence for atom # 2 N, 4, is greater than permitted
[09:45:24] Explicit valence for atom # 19 N, 4, is greater than permitted
[09:45:24] ERROR: Could not sanitize molecule ending on line 289336
[09:45:24] ERROR: Explicit valence for atom # 19 N, 4, is greater than permitted
[09:45:24] Explicit valence for atom # 18 O, 3, is greater than permitted
[09:45:24] ERROR: Could not sanitize molecule ending on line 289499
[09:45:24] ERROR: Explicit valence for atom # 18 O, 3, is greater than permitted
[09:45:24] Explicit valence for atom # 39 N, 4, is greater than permitted
[09:45:24] ERROR: Could not sanitize molecule ending on line 289952
[09:45:24] ERROR: Explicit valence for atom # 39 N, 4, is greater than permitted
'''