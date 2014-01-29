"""
<Program Name>
  update_crontab_entry.py

<Started>
  October 2, 2009

<Author>
  Zachary Boka

<Purpose>
  Modifies the current crontab entry to reflect the new 2009 seattle crontab
  entry which uses the "@reboot" directive which will use cron to start seattle
  only upon machine boot.  If there is currently no entry for seattle in the
  crontab, then this function does not add nor modify the crontab.
"""
# Python modules
import subprocess
import os
import tempfile

# Seattle modules
import nonportable
import servicelogger


SEATTLE_FILES_DIR = os.path.realpath(".")


def find_mount_point_of_seattle_dir():
  """
  <Purpose>
    Find the mount point of the directory in which seattle is currently being
    installed.

  <Arguments>
    None.

  <Excpetions>
    None.

  <Side Effects>
    None.

  <Return>
    The mount point for the directory in which seattle is currently being
    installed.
  """

  potential_mount_point = SEATTLE_FILES_DIR

  # To prevent a potential, yet unlikely, infinite loop from occuring, exit the
  # while loop if the current potential mount point is the same as
  # os.path.dirname(potential_mount_point).
  while not os.path.ismount(potential_mount_point) \
        and potential_mount_point != os.path.dirname(potential_mount_point):
    potential_mount_point = os.path.dirname(potential_mount_point)

  return potential_mount_point
      



def modify_seattle_crontab_entry():
  """
  <Purpose>
    Replaces the current seattle crontab entry, if it exists, with the updated
    entry which uses the directive @reboot to specify that cron should only
    start seattle at machine boot.

  <Arguments>
    None.

  <Exceptions>
    OSError if cron is not installed on this system?
    IOError if there is a problem creating or writing to the temporary file?

  <Side Effects>
    Modifies the seattle crontab entry, should it exist.

  <Returns>
    True if modification succeeded,
    False otherwise.
  """

  try:
    crontab_contents = subprocess.Popen(["crontab","-l"],stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
    crontab_contents_stdout = crontab_contents.stdout
  except Exception,e:
    # User does not have access to crontab, so do nothing and return.
    return False
  else:
    # Get the service vessel where any cron errors or output for seattle will
    # be written.
    service_vessel = servicelogger.get_servicevessel()

    # Get the mount point for the directory in which seattle is installed.
    mount_point = find_mount_point_of_seattle_dir()

    # Create the replacement crontab entry.
    seattle_files_dir = os.path.realpath(".")
    cron_line_entry = '@reboot if [ -e "' + SEATTLE_FILES_DIR + os.sep \
        + 'start_seattle.sh" ]; then "' + SEATTLE_FILES_DIR + os.sep \
        + 'start_seattle.sh" >> "' + SEATTLE_FILES_DIR + os.sep \
        + service_vessel + '/cronlog.txt" 2>&1; elif [ "`mount | ' \
        + 'grep -e \'[ ]' + mount_point + '[/]*[ ]\'`" = "" ]; then ' \
        + 'while [ "`mount | grep -e \'[ ]' + mount_point \
        + '[/]*[ ]\'`" = ""]; do sleep 60s; done && "' + SEATTLE_FILES_DIR \
        + os.sep + 'start_seattle.sh" >> "' + SEATTLE_FILES_DIR \
        + os.sep + service_vessel + '/cronlog.txt" 2>&1; else ' \
        + 'modifiedCrontab=`mktemp -t tempcrontab.XXXXX` && crontab -l | ' \
        + 'sed \'/start_seattle.sh/d\' > ${modifiedCrontab} && ' \
        + 'crontab ${modifiedCrontab} && rm -rf ${modifiedCrontab}; fi' \
        + os.linesep



    # Generate a temporary crontab file, and only add the new seattle crontab
    # entry if there is currently an outdated seattle crontab entry.
    temp_crontab_file = tempfile.NamedTemporaryFile()
    outdated_seattle_entry_existed = False
    for line in crontab_contents_stdout:
      if "start_seattle.sh" in line:
        line = cron_line_entry
        outdated_seattle_entry_existed = True
      temp_crontab_file.write(line)
    temp_crontab_file.flush()
    

    # If there was no outdated seattle entry, close the temporary file and
    # return.
    if not outdated_seattle_entry_existed:
      temp_crontab_file.close()
      return


    # Now, replace the crontab with that temp file and remove(close) the
    # tempfile.
    replace_crontab = subprocess.Popen(["crontab",temp_crontab_file.name],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
    replace_crontab.wait()                                    
    temp_crontab_file.close()


    # Lastly, check that the modificaiton succeeded.
    return check_modification_succeeded()




def check_modification_succeeded():
  """
  <Purpose>
    Checks that the modified crontab entry for the 2009 installer succeeded.

  <Arguments>
    None.

  <Exceptions>
    OSError if cron is not installed on this system?
    IOError if there is a problem creating or writing to the temporary file?

  <Side Effects>
    None.

  <Returns>
    True if modification succeeded,
    False otherwise.
  """
  try:
    modified_crontab_contents = \
        subprocess.Popen(["crontab","-l"],stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    modified_crontab_contents_stdout = modified_crontab_contents.stdout
  except Exception,e:
    # User does not have access to crontab, so return False.
    return False
  else:
    for line in modified_crontab_contents_stdout:
      if "@reboot" in line and "start_seattle.sh" in line:
        return True

    # Reaching this point means that the keywords in the updated seattle crontab
    # entry were not found, meaning the current crontab entry was not updated.
    return False




def main():
  """
  <Purpose>
    Test the operating system.  If this a Linux or Darwin machine, change the
    seattle crontab entry if it exists.

  <Arguments>
    None.

  <Exceptions>
    None.

  <Side Effects>
    Modifies the seattle crontab entry if it exists.

  <Returns>
    None.
  """

  if not nonportable.ostype == "Linux" and not nonportable.ostype == "Darwin":
    return
  else:
    modified_crontab = modify_seattle_crontab_entry()




if __name__ == "__main__":
  main()
