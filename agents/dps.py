from subagent.heuristics import *
from subagent.smallpreflop import SPreflopper as pre
from subagent.smallpostflop import SPostflopper as post
from subagent.oracleflop import OracleFlop as OF
from agents.deep_player import DeepPlayer
from functools import partial
from random import sample

class Post1(post):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, heur = [FLOPCALL, TURNCALL, RIVERCALL], **kwargs)

class Post2(post):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, heur = [FLOPCALL2, TURNCALL2, RIVERCALL], **kwargs)

class Pre2(pre):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, heur = PRECALL, **kwargs)

class Pre3(pre):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def rrange(self, u, **kwargs):
        return sample(list(range(15, u)), 5)

class Pre3(pre):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, raiseportions = [1.2, 0.75, 0.4, 0.2], **kwargs)

class Post3(post):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, raiseportions = [1.2, 0.75, 0.4, 0.2], **kwargs)

class Pre4(pre):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, heur = PRECALL, raiseportions = [1.25, 0.75, 0.45], **kwargs)

class Pre5(OF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, heur = PRECALL, raiseportions = [0.77, 0.53, 0.36], **kwargs)

class Pre6(OF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, heur = PRECALL2, **kwargs)

class Pre8(OF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, heur = PRECALL3, raiseportions = [1.1, 0.78, 0.51, 0.34], **kwargs)

class Post8(post):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, heur = [FLOPCALL3, TURNCALL3, RIVERCALL], **kwargs)

class Pre11(OF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, heur = PRECALL4, raiseportions = [1.1, 0.78, 0.51, 0.34], **kwargs)

class Post11(post):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, heur = [FLOPCALL4, TURNCALL4, RIVERCALL], **kwargs)

class Post16(post):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, heur = [FLOPCALL5, TURNCALL5, RIVERCALL], **kwargs)

class Dp0(DeepPlayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, preTemplate = pre, postTemplate = post, **kwargs)

class Dp1(DeepPlayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, preTemplate = pre, postTemplate = Post1, **kwargs)

class Dp2(DeepPlayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, preTemplate = Pre2, postTemplate = post, **kwargs)

class Dp3(DeepPlayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, preTemplate = Pre3, postTemplate = Post3, **kwargs)

class Dp4(DeepPlayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, preTemplate = Pre4, postTemplate = Post1, **kwargs)

class Dp5(DeepPlayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, preTemplate = Pre5, postTemplate = Post1, **kwargs)

class Dp6(DeepPlayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, preTemplate = Pre6, postTemplate = Post2, **kwargs)

class Dp7(DeepPlayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, preTemplate = OF, postTemplate = Post2, **kwargs)

class Dp8(DeepPlayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, preTemplate = Pre8, postTemplate = Post8, **kwargs)

class Dp9(DeepPlayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, preTemplate = OF, postTemplate = Post8, **kwargs)

class Dp10(DeepPlayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, preTemplate = Pre8, postTemplate = Post2, **kwargs)

class Dp11(DeepPlayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, preTemplate = Pre11, postTemplate = Post11, **kwargs)

class Dp12(DeepPlayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, preTemplate = Pre11, postTemplate = Post2, **kwargs)

class Dp13(DeepPlayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, preTemplate = Pre11, postTemplate = Post8, **kwargs)

class Dp14(DeepPlayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, preTemplate = OF, postTemplate = Post2, **kwargs)

class Dp15(DeepPlayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, preTemplate = OF, postTemplate = Post11, **kwargs)

class Dp16(DeepPlayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, preTemplate = OF, postTemplate = Post16, **kwargs)


dps = [Dp0, Dp1, Dp2, Dp4]
def setup_ai(*args, id = 0, **kwargs):
    return dps[id](*args, **kwargs)

