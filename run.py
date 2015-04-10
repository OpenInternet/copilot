# -*- coding: utf-8 -*-

import os
from copilot import app
from blockpage import blockpage

if __name__ == '__main__':
    #Start Admin Interface
    admin_port = int(os.environ.get("PORT", 8080))
    app.run('0.0.0.0', port=admin_port)
    #Start blockpage
    block_port = int(os.environ.get("PORT", 80))
    blockpage.run('0.0.0.0', port=block_port)
