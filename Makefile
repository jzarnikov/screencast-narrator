COMMON := api/common
PY_GEN := api/python-client/src/screencast_narrator_client/generated
TS_GEN := api/typescript-client/src/generated

.PHONY: generate generate-python generate-typescript generate-java test test-clients test-typescript test-java release

generate: generate-python generate-typescript
	@echo "Done."

generate-python: $(PY_GEN)/storyboard_types.py $(PY_GEN)/config_types.py $(PY_GEN)/__init__.py

$(PY_GEN)/storyboard_types.py: $(COMMON)/storyboard-schema.json
	@mkdir -p $(PY_GEN)
	datamodel-codegen \
		--input $< \
		--output-model-type pydantic_v2.BaseModel \
		--use-standard-collections \
		--use-union-operator \
		--target-python-version 3.11 \
		--snake-case-field \
		--allow-population-by-field-name \
		--output $@

$(PY_GEN)/config_types.py: $(COMMON)/config-schema.json
	@mkdir -p $(PY_GEN)
	datamodel-codegen \
		--input $< \
		--output-model-type pydantic_v2.BaseModel \
		--use-standard-collections \
		--use-union-operator \
		--target-python-version 3.11 \
		--snake-case-field \
		--allow-population-by-field-name \
		--output $@

$(PY_GEN)/__init__.py: $(PY_GEN)/storyboard_types.py $(PY_GEN)/config_types.py
	@printf '%s\n' \
		'"""Generated types from JSON schemas — do not edit manually."""' \
		'' \
		'from screencast_narrator_client.generated.config_types import (' \
		'    HighlightConfig as HighlightConfigGenerated,' \
		'    Model as ConfigModel,' \
		'    RecordingConfig,' \
		')' \
		'from screencast_narrator_client.generated.storyboard_types import (' \
		'    HighlightStyle,' \
		'    Model as StoryboardModel,' \
		'    Narration,' \
		'    Options,' \
		'    ScreenAction,' \
		'    ScreenActionTiming,' \
		'    ScreenActionType,' \
		')' \
		'' \
		'__all__ = [' \
		'    "ConfigModel",' \
		'    "HighlightConfigGenerated",' \
		'    "HighlightStyle",' \
		'    "Narration",' \
		'    "Options",' \
		'    "RecordingConfig",' \
		'    "ScreenAction",' \
		'    "ScreenActionTiming",' \
		'    "ScreenActionType",' \
		'    "StoryboardModel",' \
		']' > $@

generate-typescript: $(TS_GEN)/storyboard-types.ts $(TS_GEN)/config-types.ts

$(TS_GEN)/storyboard-types.ts: $(COMMON)/storyboard-schema.json
	@mkdir -p $(TS_GEN)
	npx json-schema-to-typescript --unreachableDefinitions $< > $@

$(TS_GEN)/config-types.ts: $(COMMON)/config-schema.json
	@mkdir -p $(TS_GEN)
	npx json-schema-to-typescript --unreachableDefinitions $< > $@

generate-java:
	mvn generate-sources -f api/java-client/pom.xml

test: test-clients
	DYLD_LIBRARY_PATH=/opt/homebrew/lib pytest

test-clients: test-typescript test-java

test-typescript:
	cd api/typescript-client && npm test

test-java:
	cd api/java-client && mvn test -q

build-java:
	cd api/java-client && mvn package -q -DskipTests

trigger-jitpack:
	@VERSION=$$(git describe --tags --abbrev=0 2>/dev/null) && \
	echo "Triggering JitPack build for $$VERSION..." && \
	curl -s "https://jitpack.io/com/github/mmarinschek/screencast-narrator/$$VERSION/screencast-narrator-$$VERSION.pom" > /dev/null && \
	echo "Waiting for JitPack build..." && \
	for i in $$(seq 1 60); do \
		STATUS=$$(curl -s "https://jitpack.io/api/builds/com.github.mmarinschek/screencast-narrator/$$VERSION" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))"); \
		if [ "$$STATUS" = "ok" ]; then \
			echo "JitPack build succeeded for $$VERSION"; \
			exit 0; \
		elif [ "$$STATUS" = "Error" ]; then \
			echo "JitPack build FAILED for $$VERSION"; \
			echo "Check https://jitpack.io/#mmarinschek/screencast-narrator/$$VERSION"; \
			exit 1; \
		fi; \
		sleep 5; \
	done; \
	echo "JitPack build timed out"; exit 1
