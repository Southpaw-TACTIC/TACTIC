###########################################################
#
# Copyright (c) 2012, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

export LD_PRELOAD=/usr/lib64/libpython2.6.so
export CLASSPATH=.:jackson-core-asl-1.9.4.jar:jackson-mapper-asl-1.9.4.jar:jep.jar

javac tactic/TacticServerStub.java
javac tactic/TacticTest.java
javac Example.java



