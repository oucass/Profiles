from pycallgraph2 import PyCallGraph
from pycallgraph2.output import GraphvizOutput
from pycallgraph2 import Config
from pycallgraph2 import GlobbingFilter
from profiles.Profile_Set import Profile_Set
import cProfile, pstats, io
from pstats import SortKey


pr = cProfile.Profile()
pr.enable()

config = Config(max_depth=10)
config.trace_filter = GlobbingFilter(exclude=[
    'SourceFileLoader.*',
    'ModuleSpec.*',
    '_*',
    ],
    include=[
        'pint.*',
        'Pint.*',
    ]
)

with PyCallGraph(output=GraphvizOutput()):
    a = Profile_Set(resolution=1, res_units='m', ascent=True, dev=True,
                    profile_start_height=400, confirm_bounds=False)
    a.add_all_profiles("/home/jessica/GitHub/data_templates/01082020"
                       "/00000108.BIN")
    at = []
    for p in a.profiles:
        at.append(p.get_thermo_profile())

    aw = []
    for p in a.profiles:
        aw.append(p.get_wind_profile())

pr.disable()
s = io.StringIO()
sortby = SortKey.TIME
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
print(s.getvalue())
