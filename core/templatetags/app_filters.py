from django import template

register = template.Library()

@register.filter(name="smooth_timedelta")
def smooth_timedelta(timedeltaobj):
    """Convert a datetime.timedelta object into Days, Hours, Minutes, Seconds."""
    secs = timedeltaobj.total_seconds()
    return "{} days".format(int(secs//86400))

