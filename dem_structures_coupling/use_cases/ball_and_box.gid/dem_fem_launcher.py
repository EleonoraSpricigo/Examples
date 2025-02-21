from __future__ import print_function, absolute_import, division #makes KratosMultiphysics backward compatible with python 2.6 and 2.7

import sys
import KratosMultiphysics as Kratos
from Kratos import Logger
import KratosMultiphysics.DEMApplication as Dem
import KratosMultiphysics.LinearSolversApplication as ExternalSolvers
import KratosMultiphysics.StructuralMechanicsApplication as Structural
import KratosMultiphysics.DemStructuresCouplingApplication as DemFem
import dem_fem_coupling_algorithm

dem_fem_coupling_algorithm.Algorithm().Run()
