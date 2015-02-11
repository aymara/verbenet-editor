import io
import sys
import traceback
from collections import defaultdict, OrderedDict

from django.http import HttpResponse
from django.template import RequestContext, loader

from syntacticframes.models import VerbNetFrame
from export.export import merge_primary_and_syntax, WrongFrameException


def errors(request):
    issues = defaultdict(list)
    frames_ok, frames_total = 0, 0

    for db_frame in VerbNetFrame.objects.select_related('frameset', 'frameset__verbnet_class', 'frameset__verbnet_class__levin_class').filter(removed=False):
        if db_frame.removed or db_frame.frameset.removed:
            continue

        frames_total += 1
        output = io.StringIO()
        try:
            merge_primary_and_syntax(db_frame.syntax, db_frame.roles_syntax, output)
            frames_ok += 1
        except WrongFrameException as e:
            issues[e.args[0]].append(db_frame)
        except Exception as e:
            exc_type, exc_value, exc_tb = sys.exc_info()
            tb_info = traceback.extract_tb(exc_tb)
            filename, line, func, text = tb_info[-1]
            exception = traceback.format_exception_only(exc_type, exc_value)[0]
            issues['{} (ligne {})'.format(exception, line)].append(db_frame)


    template = loader.get_template('errors.html')
    context = RequestContext(request, {
        'issues': OrderedDict(sorted(issues.items(), reverse=True, key=lambda kv: len(kv[1]))),
        'frames_ok': frames_ok,
        'frames_total': frames_total,
        'ratio': '{:.1%}'.format(frames_ok / frames_total),
    })

    return HttpResponse(template.render(context))
