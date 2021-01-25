

"""
Exception, Warning, and Assert errors used in Crewml project
"""




class CrewmlError(Exception):
    """
    The root exception for all crewml errors.
    """
    pass




class CrewmlDataError(CrewmlError):
    """
    Error when dealing with Crewml data
    """
    pass


class CrewmlTypeError(CrewmlError, TypeError):
    """
    Unexpected type or None for a property or input.
    """
    pass


class CrewmlValueError(CrewmlError, ValueError):
    """
    A bad value was passed into a function.
    """
    pass





class CrewmlAttributeError(CrewmlError, AttributeError):
    """
    Attribute is not passed to a function
    """
    pass


'''
Crewml Assert warning classes
'''
class CrewmlAssertionError(CrewmlError, AssertionError):
    """
    Crewml specific assert error
    """
    pass



'''
Crewml  warning classes
'''
class CrewmlWarning(UserWarning):
    """
    Generic Crewml warning
    """
    pass


class DataWarning(CrewmlWarning):
    """
     Warning realted to Crewml data
    """
    pass
