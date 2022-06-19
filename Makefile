.DEFAULT_GOAL := compile

.PHONY: requirements
requirements:
	pip install -r dev-requirements.txt
	pip install -r requirements.txt

.PHONY: tests
tests:
	python -m unittest

.PHONY: lint
lint:
	printf "Linter should be implemented\n"

.PHONY: build
build: requirements tests lint
	python3 setup.py bdist_wheel

.PHONY: --deploy_release
--deploy_release: clean build
	twine upload --repository nexus_releases dist/*.whl

.PHONY: deploy_snapshot
deploy_snapshot: clean build
	twine upload --repository nexus_snapshots dist/*.whl

.PHONY: --store_minor_version
--store_minor_version:
	$(eval CURRENT_VERSION=$(shell python setup.py -v-minor))

.PHONY: --store_micro_version
--store_micro_version:
	$(eval CURRENT_VERSION=$(shell python setup.py -v-micro))

.PHONY:
--store_full_version:
	$(eval CURRENT_VERSION=$(shell python setup.py -v-full))

.PHONY: --store_setup_py
--store_setup_py:
	cp setup.py setup_original.py

.PHONY: --restore_setup_py
--restore_setup_py:
	rm setup.py
	cp setup_original.py setup.py
	rm setup_original.py

.PHONY: --reset_to_only_minor_version
--reset_to_only_minor_version:
	sed -ri 's/(\s*snapshot_version\s*=\s*.[0-9]+\.)([0-9]+)(\.)([0-9]+)(\.)([0-9]+)(.*)/\1\2\7/g' setup.py

.PHONY: --reset_to_only_micro_version
--reset_to_only_micro_version:
	sed -ri 's/(\s*snapshot_version\s*=\s*.[0-9]+\.)([0-9]+)(\.)([0-9]+)(\.)([0-9]+)(.*)/\1\2\3\4\7/g' setup.py

.PHONY: --promote_build
--promote_build:
	sed -ri 's/(\s*snapshot_version\s*=\s*.[0-9]+\.)([0-9]+)(\.)([0-9]+)(\.)([0-9]+)(.*)/echo "\1\2\3\4\5$$((\6+1))\7"/ge' setup.py

.PHONY: --scm_bump_build
--scm_bump_build:
	git add setup.py
	git commit -m 'AUTO-BUILD $(CURRENT_VERSION)'
	git push $(GIT_REMOTE)

.PHONY: --check_git_remote_defined
--check_git_remote_defined:
	test -n "$(GIT_REMOTE)"

.PHONY: ci_build
ci_build:	--check_git_remote_defined\
					deploy_snapshot\
 					--store_full_version\
 					--promote_build\
 					--scm_bump_build

.PHONY: --promote_micro
--promote_micro:
	sed -ri 's/(\s*snapshot_version\s*=\s*.[0-9]+\.)([0-9]+)(\.)([0-9]+)(\.)([0-9]+)(.*)/echo "\1\2\3$$((\4+1))\50\7"/ge' setup.py

.PHONY: --scm_bump_patch
--scm_bump_patch:
	git add setup.py
	git commit -m 'AUTO-MICRO-RELEASE $(CURRENT_VERSION)'
	git push $(GIT_REMOTE) --follow-tags

.PHONY: --scm_patch_tag
--scm_patch_tag:
	git tag -a 'v$(CURRENT_VERSION)-MICRO-RELEASE-TAG' -m 'AUTO-MICRO-RELEASE'

.PHONY: --check_patch_branch
--check_patch_branch:
	test $$(git branch -l | grep '*' | tr -d '*' | xargs | sed -r 's/(.*)(RELEASE-BRANCH)/\2/g') = 'RELEASE-BRANCH'

.PHONY: micro_release
micro_release:	--check_git_remote_defined\
				--check_patch_branch\
				--store_setup_py\
				--reset_to_only_micro_version\
 				--deploy_release\
 				--restore_setup_py\
 				--store_micro_version\
 				--scm_patch_tag\
 				--promote_micro\
 				--scm_bump_patch

.PHONY: --promote_minor
--promote_minor:
	sed -ri 's/(\s*snapshot_version\s*=\s*.[0-9]+\.)([0-9]+)(\.)([0-9]+)(\.)([0-9]+)(.*)/echo "\1$$((\2+1))\30\50\7"/ge' setup.py

.PHONY: --scm_bump_release
--scm_bump_release:
	git add setup.py
	git commit -m 'AUTO-RELEASE $(CURRENT_VERSION)'
	git push $(GIT_REMOTE) --follow-tags

.PHONY: --scm_release_tag
--scm_release_tag:
	git tag -a 'v$(CURRENT_VERSION)-RELEASE-TAG' -m 'AUTO-RELEASE'

.PHONY: --start_patch_branch
--start_patch_branch:
	git checkout -b 'v$(CURRENT_VERSION)-RELEASE-BRANCH'

.PHONY: --push_started_patch
--push_started_patch:
	git add setup.py
	git commit -m 'v$(CURRENT_VERSION)-MICRO-RELEASE-START'
	git push $(GIT_REMOTE) -u 'v$(CURRENT_VERSION)-RELEASE-BRANCH'
	git checkout master

.PHONY: --check_master
--check_master:
	test $$(git branch -l | grep '*' | tr -d '*' | xargs) = 'master'

.PHONY: release
release:	--check_git_remote_defined\
					--check_master\
					--store_setup_py\
					--reset_to_only_minor_version\
					--deploy_release\
					--restore_setup_py\
					--store_minor_version\
					--scm_release_tag\
					--start_patch_branch\
					--promote_micro\
					--push_started_patch\
					--promote_minor\
					--scm_bump_release

.PHONY: clean
clean:
	rm -rf dist build .hypothesis *.egg-info
