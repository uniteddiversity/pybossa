# -*- coding: utf8 -*-
# This file is part of PyBossa.
#
# Copyright (C) 2014 SF Isle of Man Limited
#
# PyBossa is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyBossa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with PyBossa.  If not, see <http://www.gnu.org/licenses/>.
from default import db
from helper import web
from pybossa.jobs import import_tasks
from factories import AppFactory
from pybossa.repositories import UserRepository
from pybossa.repositories import ProjectRepository
from mock import patch, MagicMock
from mock import patch

project_repo = ProjectRepository(db)
user_repo = UserRepository(db)

class TestAutoimporterAccessAndResponses(web.Helper):

    def test_autoimporter_get_redirects_to_login_if_anonymous(self):
        """Test task autoimporter endpoint requires login"""
        app = AppFactory.create()
        url = "/app/%s/tasks/autoimporter" % app.short_name

        res = self.app.get(url)
        redirect_url = 'http://localhost/account/signin?next='
        assert res.status_code == 302, res.status_code
        assert redirect_url in res.location, res.location


    def test_autoimporter_get_forbidden_non_owner(self):
        """Test task autoimporter returns Forbidden if non owner accesses"""
        self.register()
        self.new_application()
        app = project_repo.get(1)
        self.signout()
        self.register(name='non-owner')
        url = "/app/%s/tasks/autoimporter" % app.short_name

        res = self.app.get(url)

        assert res.status_code == 403, res.status_code


    def test_autoimporter_get_forbidden_owner_no_pro(self):
        """Test task autoimporter returns Forbidden if no pro accesses"""
        self.register()
        self.signout()
        # User
        self.register(name="owner")
        self.new_application()
        app = project_repo.get(1)
        url = "/app/%s/tasks/autoimporter" % app.short_name

        res = self.app.get(url, follow_redirects=True)
        assert  res.status_code == 403, res.status_code


    def test_autoimporter_get_owner_pro(self):
        """Test task autoimporter works for pro user"""
        self.register()
        self.signout()
        # User
        self.register(name="owner")
        owner = user_repo.get_by_name("owner")
        owner.pro = True
        user_repo.save(owner)

        self.new_application()
        app = project_repo.get(1)
        url = "/app/%s/tasks/autoimporter" % app.short_name

        res = self.app.get(url, follow_redirects=True)
        assert  res.status_code == 200, res.status_code


    def test_autoimporter_get_admin(self):
        """Test task autoimporter works for admin user"""
        self.register()
        self.signout()
        # User
        self.register(name="owner")
        self.new_application()
        self.signout()
        self.signin()
        app = project_repo.get(1)
        url = "/app/%s/tasks/autoimporter" % app.short_name

        res = self.app.get(url, follow_redirects=True)
        assert  res.status_code == 200, res.status_code


    def test_autoimporter_get_nonexisting_project(self):
        """Test task autoimporter to a non existing project returns 404"""
        self.register()
        res = self.app.get("/app/noExists/tasks/autoimporter")

        assert res.status_code == 404, res.status_code


    def test_autoimporter_post_redirects_to_login_if_anonymous(self):
        """Test task autoimporter endpoint post requires login"""
        app = AppFactory.create()
        url = "/app/%s/tasks/autoimporter" % app.short_name

        res = self.app.post(url, data={})
        redirect_url = 'http://localhost/account/signin?next='
        assert res.status_code == 302, res.status_code
        assert redirect_url in res.location, res.location


    def test_autoimporter_post_forbidden_non_owner(self):
        """Test task autoimporter post returns Forbidden if non owner accesses"""
        self.register()
        self.new_application()
        app = project_repo.get(1)
        self.signout()
        self.register(name='non-owner')
        url = "/app/%s/tasks/autoimporter" % app.short_name

        res = self.app.post(url, data={})

        assert res.status_code == 403, res.status_code


    def test_autoimporter_post_forbidden_owner_no_pro(self):
        """Test task autoimporter post returns Forbidden if no pro accesses"""
        self.register()
        self.signout()
        # User
        self.register(name="owner")
        self.new_application()
        app = project_repo.get(1)
        url = "/app/%s/tasks/autoimporter" % app.short_name

        res = self.app.post(url, data={}, follow_redirects=True)
        assert  res.status_code == 403, res.status_code


    def test_autoimporter_post_owner_pro(self):
        """Test task autoimporter post works for pro user"""
        self.register()
        self.signout()
        # User
        self.register(name="owner")
        owner = user_repo.get_by_name("owner")
        owner.pro = True
        user_repo.save(owner)

        self.new_application()
        app = project_repo.get(1)
        url = "/app/%s/tasks/autoimporter" % app.short_name

        res = self.app.post(url, data={'csv_url': 'http://as.com',
                                       'formtype': 'json', 'form_name': 'csv'},
                                       follow_redirects=True)
        assert  res.status_code == 200, res.status_code


    def test_autoimporter_post_admin(self):
        """Test task autoimporter post works for admin user"""
        self.register()
        self.signout()
        # User
        self.register(name="owner")
        self.new_application()
        self.signout()
        self.signin()
        app = project_repo.get(1)
        url = "/app/%s/tasks/autoimporter" % app.short_name

        res = self.app.post(url, data={'csv_url': 'http://as.com',
                                       'formtype': 'json', 'form_name': 'csv'},
                                       follow_redirects=True)
        assert  res.status_code == 200, res.status_code


    def test_autoimporter_post_nonexisting_project(self):
        """Test task autoimporter post to a non existing project returns 404"""
        self.register()
        res = self.app.post("/app/noExists/tasks/autoimporter", data={})

        assert res.status_code == 404, res.status_code


    def test_delete_autoimporter_post_redirects_to_login_if_anonymous(self):
        """Test delete task autoimporter endpoint requires login"""
        app = AppFactory.create()
        url = "/app/%s/tasks/autoimporter/delete" % app.short_name

        res = self.app.post(url, data={})
        redirect_url = 'http://localhost/account/signin?next='
        assert res.status_code == 302, res.status_code
        assert redirect_url in res.location, res.location


    def test_delete_autoimporter_post_forbidden_non_owner(self):
        """Test delete task autoimporter returns Forbidden if non owner accesses"""
        self.register()
        self.new_application()
        app = project_repo.get(1)
        self.signout()
        self.register(name='non-owner')
        url = "/app/%s/tasks/autoimporter/delete" % app.short_name

        res = self.app.post(url, data={})

        assert res.status_code == 403, res.status_code


    def test_delete_autoimporter_post_forbidden_owner_no_pro(self):
        """Test delete task autoimporter returns Forbidden if no pro accesses"""
        self.register()
        self.signout()
        # User
        self.register(name="owner")
        self.new_application()
        app = project_repo.get(1)
        url = "/app/%s/tasks/autoimporter/delete" % app.short_name

        res = self.app.post(url, data={}, follow_redirects=True)
        assert  res.status_code == 403, res.status_code


    def test_delete_autoimporter_post_owner_pro(self):
        """Test delete task autoimporter works for pro user"""
        self.register()
        self.signout()
        # User
        self.register(name="owner")
        owner = user_repo.get_by_name("owner")
        owner.pro = True
        user_repo.save(owner)

        self.new_application()
        app = project_repo.get(1)
        url = "/app/%s/tasks/autoimporter/delete" % app.short_name

        res = self.app.post(url, data={}, follow_redirects=True)
        assert  res.status_code == 200, res.status_code


    def test_delete_autoimporter_post_admin(self):
        """Test delete task autoimporter works for admin user"""
        self.register()
        self.signout()
        # User
        self.register(name="owner")
        self.new_application()
        self.signout()
        self.signin()
        app = project_repo.get(1)
        url = "/app/%s/tasks/autoimporter/delete" % app.short_name

        res = self.app.post(url, data={}, follow_redirects=True)
        assert  res.status_code == 200, res.status_code


    def test_delete_autoimporter_get_nonexisting_project(self):
        """Test task delete autoimporter to a non existing project returns 404"""
        self.register()
        res = self.app.post("/app/noExists/tasks/autoimporter/delete")

        assert res.status_code == 404, res.status_code



class TestAutoimporterBehaviour(web.Helper):

    def test_autoimporter_shows_template_to_create_new_if_no_autoimporter(self):
        """Test task autoimporter get renders the template for creating new
        autoimporter if none exists"""
        self.register()
        owner = user_repo.get(1)
        app = AppFactory.create(owner=owner)
        url = "/app/%s/tasks/autoimporter" % app.short_name
        expected_text = "Setup task autoimporter"

        res = self.app.get(url, follow_redirects=True)

        assert expected_text in res.data
        assert 'CSV' in res.data
        assert 'Google Drive Spreadsheet' in res.data
        assert 'EpiCollect Plus Project' in res.data
        assert 'Flickr' in res.data
        assert 'Dropbox' not in res.data


    @patch('pybossa.core.importer.get_autoimporter_names')
    def test_autoimporter_doesnt_show_unavailable_importers(self, names):
        names.return_value = ['csv', 'gdocs', 'epicollect']
        self.register()
        owner = user_repo.get(1)
        app = AppFactory.create(owner=owner)
        url = "/app/%s/tasks/autoimporter" % app.short_name

        res = self.app.get(url, follow_redirects=True)

        assert 'Flickr' not in res.data


    def test_autoimporter_with_specific_variant_argument(self):
        """Test task autoimporter with specific autoimporter variant argument
        shows the form for it, for each of the variants"""
        self.register()
        owner = user_repo.get(1)
        app = AppFactory.create(owner=owner)

        # CSV
        url = "/app/%s/tasks/autoimporter?type=csv" % app.short_name
        res = self.app.get(url, follow_redirects=True)
        data = res.data.decode('utf-8')

        assert "From a CSV file" in data
        assert 'action="/app/%E2%9C%93app1/tasks/autoimporter"' in data

        # Google Docs
        url = "/app/%s/tasks/autoimporter?type=gdocs" % app.short_name
        res = self.app.get(url, follow_redirects=True)
        data = res.data.decode('utf-8')

        assert "From a Google Docs Spreadsheet" in data
        assert 'action="/app/%E2%9C%93app1/tasks/autoimporter"' in data

        # Epicollect Plus
        url = "/app/%s/tasks/autoimporter?type=epicollect" % app.short_name
        res = self.app.get(url, follow_redirects=True)
        data = res.data.decode('utf-8')

        assert "From an EpiCollect Plus project" in data
        assert 'action="/app/%E2%9C%93app1/tasks/autoimporter"' in data

        # Flickr
        url = "/app/%s/tasks/autoimporter?type=flickr" % app.short_name
        res = self.app.get(url, follow_redirects=True)
        data = res.data.decode('utf-8')

        assert "From a Flickr Album" in data
        assert 'action="/app/%E2%9C%93app1/tasks/autoimporter"' in data

        # Dropbox
        url = "/app/%s/tasks/autoimporter?type=dropbox" % app.short_name
        res = self.app.get(url, follow_redirects=True)
        data = res.data.decode('utf-8')

        assert res.status_code == 404, res.status_code

        # Invalid
        url = "/app/%s/tasks/autoimporter?type=invalid" % app.short_name
        res = self.app.get(url, follow_redirects=True)

        assert res.status_code == 404, res.status_code


    def test_autoimporter_shows_current_autoimporter_if_exists(self):
        """Test task autoimporter shows the current autoimporter if exists"""
        self.register()
        owner = user_repo.get(1)
        autoimporter = {'type': 'csv', 'csv_url': 'http://fakeurl.com'}
        app = AppFactory.create(owner=owner, info={'autoimporter': autoimporter})
        url = "/app/%s/tasks/autoimporter" % app.short_name

        res = self.app.get(url, follow_redirects=True)

        assert "You currently have the following autoimporter" in res.data


    def test_autoimporter_post_creates_autoimporter_attribute(self):
        """Test a valid post to autoimporter endpoint sets an autoimporter to
        the project"""
        self.register()
        owner = user_repo.get(1)
        autoimporter = {'type': 'csv', 'csv_url': 'http://fakeurl.com'}
        app = AppFactory.create(owner=owner)
        url = "/app/%s/tasks/autoimporter" % app.short_name
        data = {'form_name': 'csv', 'csv_url': 'http://fakeurl.com'}

        self.app.post(url, data=data, follow_redirects=True)

        assert app.has_autoimporter() is True, app.get_autoimporter()
        assert app.get_autoimporter() == autoimporter, app.get_autoimporter()


    def test_autoimporter_prevents_from_duplicated(self):
        """Test a valid post to autoimporter endpoint will not create another
        autoimporter if one exists for that app"""
        self.register()
        owner = user_repo.get(1)
        autoimporter = {'type': 'csv', 'csv_url': 'http://fakeurl.com'}
        app = AppFactory.create(owner=owner, info={'autoimporter': autoimporter})
        url = "/app/%s/tasks/autoimporter" % app.short_name
        data = {'form_name': 'gdocs', 'googledocs_url': 'http://another.com'}

        res = self.app.post(url, data=data, follow_redirects=True)

        assert app.get_autoimporter() == autoimporter, app.get_autoimporter()


    def test_delete_autoimporter_deletes_current_autoimporter_job(self):
        self.register()
        owner = user_repo.get(1)
        autoimporter = {'type': 'csv', 'csv_url': 'http://fakeurl.com'}
        app = AppFactory.create(owner=owner, info={'autoimporter': autoimporter})
        url = "/app/%s/tasks/autoimporter/delete" % app.short_name

        res = self.app.post(url, data={}, follow_redirects=True)

        assert app.has_autoimporter() is False, app.get_autoimporter()


    def test_flickr_autoimporter_page_shows_option_to_log_into_flickr(self):
        self.register()
        owner = user_repo.get(1)
        app = AppFactory.create(owner=owner)
        url = "/app/%s/tasks/autoimporter?type=flickr" % app.short_name

        res = self.app.get(url)
        login_url = '/flickr/?next=%2Fapp%2F%25E2%259C%2593app1%2Ftasks%2Fautoimporter%3Ftype%3Dflickr'

        assert login_url in res.data


    @patch('pybossa.view.applications.flickr')
    def test_flickr_autoimporter_page_shows_albums_and_revoke_access_option(
            self, flickr):
        flickr.get_user_albums.return_value = [{'photos': u'1',
                                               'thumbnail_url': u'fake-url',
                                               'id': u'my-fake-ID',
                                               'title': u'my-fake-title'}]
        self.register()
        owner = user_repo.get(1)
        app = AppFactory.create(owner=owner)
        url = "/app/%s/tasks/autoimporter?type=flickr" % app.short_name

        res = self.app.get(url)
        revoke_url = '/flickr/revoke-access?next=%2Fapp%2F%25E2%259C%2593app1%2Ftasks%2Fautoimporter%3Ftype%3Dflickr'

        assert '1 photos' in res.data
        assert 'src="fake-url"' in res.data
        assert 'id="my-fake-ID"' in res.data
        assert 'my-fake-title' in res.data
        assert revoke_url in res.data
