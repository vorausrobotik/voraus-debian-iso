@Library('vorausPipelineUtils')
import org.voraus.PipelineUtilities
import org.voraus.VirtualEnvironment

PipelineUtilities utils = new PipelineUtilities(this)
VirtualEnvironment venv
VirtualEnvironment venvDependencies

pipeline {
  agent {
    dockerfile {
      filename 'Dockerfile'
      registryUrl 'https://artifactory.vorausrobotik.com/docker/'
      label 'docker-linux' // Only run this job on nodes that are tagged with "docker-linux"
      args '''
          -v /home/localuser/jenkins/tools:/home/localuser/jenkins/tools
          -v /home/localuser/.cache/pip:/home/jenkins/.cache/pip:rw,z
          -v /home/localuser/.cache/uv:/home/jenkins/.cache/uv:rw,z
          -v /home/localuser/.sonar/cache:/home/jenkins/.sonar/cache:rw,z
          '''
      additionalBuildArgs '--pull' // Always pull so that we ensure the correct version
    }
  }
  environment {
    // These variables determine where the artifact is published.
    // More information can be found here: https://vorausrobotik.atlassian.net/wiki/x/yoCvvw
    PROJECT = 'default'
    SCOPE = 'private'
    UV_INDEX_URL = 'https://artifactory.vorausrobotik.com/artifactory/api/pypi/pypi/simple'
  }
  stages {
    stage('Prepare env') {
      steps {
        script {
          parallel(
            'Init JFrog': {
              env.MATURITY = env.TAG_NAME != null ? 'production' : 'testing'
              env.DEPLOY_REPO = "${env.PROJECT}-pypi-${env.SCOPE}-${env.MATURITY}-onprem-local"
              utils.artifactory.initPipBuild(pythonDeployRepo: env.DEPLOY_REPO)
            },
            'Init venv': {
              venv = utils.venvFactory.createEnvironment()
              venv.executeCommand('pip install "tox==4.24.1" "tox-uv~=1.23.0"')
            },
            'Set environment variables': {
              // https://vorausrobotik.atlassian.net/browse/ESPRIT-1901
              env.SOURCE_DATE_EPOCH = sh(script: 'git log -1 --format=%ct', returnStdout: true).trim()
            },
            'Init dependency venv': {
              venvDependencies = utils.venvFactory.createEnvironment(name: 'venvDependencies')
            },
            'Abort tag builds on non-tag jobs': {
              String[] tags = sh(script: "git describe --tags --exact-match || echo ''", returnStdout: true).trim().split('\n').findAll { it }
              if (tags && env.TAG_NAME != env.BRANCH_NAME) {
                currentBuild.result = 'ABORTED'
                throw new Exception("Tag(s) detected ($tags), skipping branch build. Tag build(s) handle this.")
              }
            }
          )
        }
      }
    }
    // resolvePipDependencies triggers an uncached force re-install conflicting for the same reasons as the build step.
    stage('Populate build info') {
      steps {
        script {
          utils.artifactory.resolvePipDependencies(venv: venvDependencies)
        }
      }
    }
    // `python -m build` produces a temporary directory within the project directory containing source files.
    // All other tools might analyze them, although they're not meant to and are gone moments after indexing.
    // This leads to all kinds of issues due to this race condition.
    stage('Build package') {
      steps {
        script {
          venv.executeCommand('tox run -e build')
        }
      }
    }
    stage('Test and Docs') {
      parallel {
        stage('Run static checks') {
          steps {
            script {
              venv.executeCommand('tox run -e lint --installpkg dist/voraus_runtime-*.whl')
            }
          }
        }
        stage('Run tests') {
          steps {
            script {
              // Initialize the test environments in parallel
              venv.executeCommand('tox run-parallel -f test --notest --parallel-no-spinner --parallel-live --installpkg dist/voraus_runtime-*.whl')
              // Run the test environments in sequence in the precommissioned environments
              venv.executeCommand('tox run -f test --skip-pkg-install -- --maxfail 10')
            }
          }
        }
        stage('Build documentation') {
          steps {
            script {
              venv.executeCommand('tox run -e docs --installpkg dist/voraus_runtime-*.whl')
            }
          }
        }
      }
    }
    stage('Publish package') {
      when {
        anyOf {
          buildingTag()
          branch 'main'
        }
      }
      steps {
        script {
          utils.artifactory.uploadPypiArtifacts(artifactoryRepo: env.DEPLOY_REPO)
        }
      }
    }
    stage('Publish GitHub Release') {
      when {
        buildingTag()
      }
      steps {
        script {
          utils.release.runJReleaser(
            command: 'release',
            projectVersion: utils.git.getTag()
          )
        }
      }
    }
  }
  post {
    always {
      script {
        utils.genericStages.run()
        utils.postActions.run()
      }

      junit 'reports/pytest.xml'
      recordCoverage(
        tools: [
          [
            parser: 'COBERTURA',
            pattern: 'reports/coverage.xml'
          ]
        ]
      )
      archiveArtifacts artifacts: 'dist/**', allowEmptyArchive: true
    }
    success {
      publishHTML(
        [
          allowMissing: false,
          alwaysLinkToLastBuild: false,
          keepAll: false,
          reportDir: 'docs/build/html/',
          reportFiles: 'index.html',
          reportName: 'Documentation',
          reportTitles: ''
        ]
      )
    }
  }
}
