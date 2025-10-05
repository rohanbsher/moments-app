#!/usr/bin/env python3
"""
Generate Xcode project files programmatically for MomentsApp
"""

import os
import uuid
from pathlib import Path

# Project configuration
PROJECT_NAME = "MomentsApp"
BUNDLE_ID = "com.moments.MomentsApp"
DEPLOYMENT_TARGET = "17.0"
SWIFT_VERSION = "5.9"

# Paths
IOS_DIR = Path(__file__).parent
PROJECT_DIR = IOS_DIR / f"{PROJECT_NAME}.xcodeproj"
SOURCE_DIR = IOS_DIR / PROJECT_NAME

# Generate UUIDs for Xcode references
def gen_uuid():
    return uuid.uuid4().hex[:24].upper()

# Collect all Swift files
def collect_swift_files(source_dir):
    swift_files = []
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.swift'):
                rel_path = os.path.relpath(os.path.join(root, file), source_dir)
                swift_files.append(rel_path)
    return sorted(swift_files)

# Create pbxproj content
def create_pbxproj():
    swift_files = collect_swift_files(SOURCE_DIR)

    # Generate file references
    file_refs = {}
    for swift_file in swift_files:
        file_refs[swift_file] = {
            'uuid': gen_uuid(),
            'build_uuid': gen_uuid()
        }

    # Main IDs
    project_uuid = gen_uuid()
    main_group_uuid = gen_uuid()
    product_group_uuid = gen_uuid()
    target_uuid = gen_uuid()
    native_target_uuid = gen_uuid()
    sources_build_phase_uuid = gen_uuid()
    frameworks_build_phase_uuid = gen_uuid()
    resources_build_phase_uuid = gen_uuid()
    build_config_list_uuid = gen_uuid()
    debug_config_uuid = gen_uuid()
    release_config_uuid = gen_uuid()
    product_ref_uuid = gen_uuid()

    # Create pbxproj content
    pbxproj = f"""// !$*UTF8*$!
{{
	archiveVersion = 1;
	classes = {{
	}};
	objectVersion = 56;
	objects = {{

/* Begin PBXBuildFile section */
"""

    # Add build file entries for each Swift file
    for swift_file, ids in file_refs.items():
        pbxproj += f"\t\t{ids['build_uuid']} /* {swift_file} in Sources */ = {{isa = PBXBuildFile; fileRef = {ids['uuid']} /* {swift_file} */; }};\n"

    pbxproj += f"""/* End PBXBuildFile section */

/* Begin PBXFileReference section */
\t\t{product_ref_uuid} /* {PROJECT_NAME}.app */ = {{isa = PBXFileReference; explicitFileType = wrapper.application; includeInIndex = 0; path = {PROJECT_NAME}.app; sourceTree = BUILT_PRODUCTS_DIR; }};
"""

    # Add file references
    for swift_file, ids in file_refs.items():
        pbxproj += f"\t\t{ids['uuid']} /* {swift_file} */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = \"{swift_file}\"; sourceTree = \"<group>\"; }};\n"

    pbxproj += f"""/* End PBXFileReference section */

/* Begin PBXFrameworksBuildPhase section */
\t\t{frameworks_build_phase_uuid} /* Frameworks */ = {{
\t\t\tisa = PBXFrameworksBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};
/* End PBXFrameworksBuildPhase section */

/* Begin PBXGroup section */
\t\t{main_group_uuid} = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
\t\t\t\t{product_group_uuid} /* Products */,
"""

    # Add file references to main group
    for swift_file, ids in file_refs.items():
        pbxproj += f"\t\t\t\t{ids['uuid']} /* {swift_file} */,\n"

    pbxproj += f"""\t\t\t);
\t\t\tsourceTree = \"<group>\";
\t\t}};
\t\t{product_group_uuid} /* Products */ = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
\t\t\t\t{product_ref_uuid} /* {PROJECT_NAME}.app */,
\t\t\t);
\t\t\tname = Products;
\t\t\tsourceTree = \"<group>\";
\t\t}};
/* End PBXGroup section */

/* Begin PBXNativeTarget section */
\t\t{native_target_uuid} /* {PROJECT_NAME} */ = {{
\t\t\tisa = PBXNativeTarget;
\t\t\tbuildConfigurationList = {build_config_list_uuid} /* Build configuration list for PBXNativeTarget \"{PROJECT_NAME}\" */;
\t\t\tbuildPhases = (
\t\t\t\t{sources_build_phase_uuid} /* Sources */,
\t\t\t\t{frameworks_build_phase_uuid} /* Frameworks */,
\t\t\t\t{resources_build_phase_uuid} /* Resources */,
\t\t\t);
\t\t\tbuildRules = (
\t\t\t);
\t\t\tdependencies = (
\t\t\t);
\t\t\tname = {PROJECT_NAME};
\t\t\tproductName = {PROJECT_NAME};
\t\t\tproductReference = {product_ref_uuid} /* {PROJECT_NAME}.app */;
\t\t\tproductType = \"com.apple.product-type.application\";
\t\t}};
/* End PBXNativeTarget section */

/* Begin PBXProject section */
\t\t{project_uuid} /* Project object */ = {{
\t\t\tisa = PBXProject;
\t\t\tattributes = {{
\t\t\t\tBuildIndependentTargetsInParallel = 1;
\t\t\t\tLastSwiftUpdateCheck = 1540;
\t\t\t\tLastUpgradeCheck = 1540;
\t\t\t\tTargetAttributes = {{
\t\t\t\t\t{native_target_uuid} = {{
\t\t\t\t\t\tCreatedOnToolsVersion = 15.4;
\t\t\t\t\t}};
\t\t\t\t}};
\t\t\t}};
\t\t\tbuildConfigurationList = {build_config_list_uuid} /* Build configuration list for PBXProject \"{PROJECT_NAME}\" */;
\t\t\tcompatibilityVersion = \"Xcode 14.0\";
\t\t\tdevelopmentRegion = en;
\t\t\thasScannedForEncodings = 0;
\t\t\tknownRegions = (
\t\t\t\ten,
\t\t\t\tBase,
\t\t\t);
\t\t\tmainGroup = {main_group_uuid};
\t\t\tproductRefGroup = {product_group_uuid} /* Products */;
\t\t\tprojectDirPath = \"\";
\t\t\tprojectRoot = \"\";
\t\t\ttargets = (
\t\t\t\t{native_target_uuid} /* {PROJECT_NAME} */,
\t\t\t);
\t\t}};
/* End PBXProject section */

/* Begin PBXResourcesBuildPhase section */
\t\t{resources_build_phase_uuid} /* Resources */ = {{
\t\t\tisa = PBXResourcesBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};
/* End PBXResourcesBuildPhase section */

/* Begin PBXSourcesBuildPhase section */
\t\t{sources_build_phase_uuid} /* Sources */ = {{
\t\t\tisa = PBXSourcesBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
"""

    # Add build files
    for swift_file, ids in file_refs.items():
        pbxproj += f"\t\t\t\t{ids['build_uuid']} /* {swift_file} in Sources */,\n"

    pbxproj += f"""\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};
/* End PBXSourcesBuildPhase section */

/* Begin XCBuildConfiguration section */
\t\t{debug_config_uuid} /* Debug */ = {{
\t\t\tisa = XCBuildConfiguration;
\t\t\tbuildSettings = {{
\t\t\t\tALWAYS_SEARCH_USER_PATHS = NO;
\t\t\t\tCLANG_ENABLE_MODULES = YES;
\t\t\t\tCOPY_PHASE_STRIP = NO;
\t\t\t\tENABLE_TESTABILITY = YES;
\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = {DEPLOYMENT_TARGET};
\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = {BUNDLE_ID};
\t\t\t\tPRODUCT_NAME = \"$(TARGET_NAME)\";
\t\t\t\tSWIFT_VERSION = {SWIFT_VERSION};
\t\t\t\tTARGETED_DEVICE_FAMILY = \"1,2\";
\t\t\t}};
\t\t\tname = Debug;
\t\t}};
\t\t{release_config_uuid} /* Release */ = {{
\t\t\tisa = XCBuildConfiguration;
\t\t\tbuildSettings = {{
\t\t\t\tALWAYS_SEARCH_USER_PATHS = NO;
\t\t\t\tCLANG_ENABLE_MODULES = YES;
\t\t\t\tCOPY_PHASE_STRIP = YES;
\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = {DEPLOYMENT_TARGET};
\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = {BUNDLE_ID};
\t\t\t\tPRODUCT_NAME = \"$(TARGET_NAME)\";
\t\t\t\tSWIFT_VERSION = {SWIFT_VERSION};
\t\t\t\tTARGETED_DEVICE_FAMILY = \"1,2\";
\t\t\t}};
\t\t\tname = Release;
\t\t}};
/* End XCBuildConfiguration section */

/* Begin XCConfigurationList section */
\t\t{build_config_list_uuid} /* Build configuration list for PBXNativeTarget \"{PROJECT_NAME}\" */ = {{
\t\t\tisa = XCConfigurationList;
\t\t\tbuildConfigurations = (
\t\t\t\t{debug_config_uuid} /* Debug */,
\t\t\t\t{release_config_uuid} /* Release */,
\t\t\t);
\t\t\tdefaultConfigurationIsVisible = 0;
\t\t\tdefaultConfigurationName = Release;
\t\t}};
/* End XCConfigurationList section */
\t}};
\trootObject = {project_uuid} /* Project object */;
}}
"""

    return pbxproj

# Main execution
if __name__ == "__main__":
    print("🔨 Generating Xcode project for MomentsApp...")
    print(f"📁 Project directory: {PROJECT_DIR}")
    print(f"📱 Bundle ID: {BUNDLE_ID}")
    print(f"🎯 Deployment target: iOS {DEPLOYMENT_TARGET}")
    print("")

    # Create project directory
    PROJECT_DIR.mkdir(exist_ok=True)

    # Generate pbxproj
    print("📝 Generating project.pbxproj...")
    pbxproj_content = create_pbxproj()

    # Write pbxproj file
    pbxproj_path = PROJECT_DIR / "project.pbxproj"
    with open(pbxproj_path, 'w') as f:
        f.write(pbxproj_content)

    print(f"✅ Created: {pbxproj_path}")
    print("")
    print("✨ Xcode project generated successfully!")
    print("")
    print("Next steps:")
    print("  1. cd ios")
    print("  2. xcodebuild -project MomentsApp.xcodeproj -scheme MomentsApp -sdk iphonesimulator")
    print("")
