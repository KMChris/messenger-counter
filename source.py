from zipfile import ZipFile
import os


class Source:
    """
    Read data from given .zip file or
    the directory from extracted .zip file.
    """
    def __init__(self, path):
        folders = ['inbox', 'archived_threads',
                   'filtered_threads', 'message_requests']

        # Detecting if path is .zip file or directory
        if path.endswith('.zip'):
            self.zip = ZipFile(path)
            self.path = 'your_activity_across_facebook/messages/'
            self.paths = [self.path + folder + '/'
                          for folder in folders]
        elif os.path.isdir(path):
            self.zip = None
            # Find messages folder
            for root, dirs, files in os.walk(path):
                if 'messages' in dirs:
                    self.path = os.path.join(root, 'messages')
                    self.paths = [os.path.join(self.path, folder)
                                  for folder in folders]
                    break
            else:
                raise FileNotFoundError('Messages not found.')
        else:
            raise FileNotFoundError('Path is not a .zip file or directory.')

        self.senders = self._get_senders()
        self.files = {sender: self._get_files(sender)
                      for sender in self.senders}

    def open(self, file):
        """
        Extracts file from .zip file
        or opens file from the directory.
        """
        if self.zip is not None:
            return self.zip.open(file)
        return open(os.path.join(file), 'rb')

    def _get_senders(self):
        """
        Returns set containing ids
        of all conversations.
        """
        if self.zip is not None:
            return {x.split('/')[3] for x in self.zip.namelist()
                    if any(x.endswith('/') and x.startswith(path)
                           and x != path for path in self.paths)}
        return {d for path in self.paths
                for d in os.listdir(path)}

    def _get_files(self, sender):
        """
        Returns list of paths to .json files
        containing messages from specific sender.
        """
        if self.zip is not None:
            return [x for path in self.paths for x in self.zip.namelist()
                    if x.endswith('.json') and x.startswith(path + sender + '/message_')]
        # Check in which folder is the sender
        for path in self.paths:
            if sender in os.listdir(path):
                # Return all .json files in the folder
                files = os.listdir(os.path.join(path, sender))
                return [os.path.join(path, sender, file)
                        for file in files
                        if file.endswith('.json')]
        raise FileNotFoundError('Sender not found.')

    def close(self):
        if self.zip is not None:
            self.zip.close()
