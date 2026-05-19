class Gorz < Formula
  desc "Local-first Gorz prototype launcher for confidence-aware messaging"
  homepage "https://github.com/pirbod/gozar"
  url "https://github.com/pirbod/gozar/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "REPLACE_WITH_RELEASE_TARBALL_SHA256"
  license "MIT"

  depends_on "git"
  depends_on "python@3.12"
  depends_on "docker" => :recommended

  def install
    bin.install "bin/gorz"
  end

  def caveats
    <<~EOS
      Gorz is a local-first prototype launcher.

      Start the local demo:
        gorz demo

      Open:
        Web:      http://localhost:5174
        API:      http://localhost:8090/api/gorz/health
        API docs: http://localhost:8090/docs

      Requirements:
        Docker Desktop or Docker Engine with the Compose plugin must be running.

      Safety:
        This is not a production secure messenger, not a circumvention tool,
        and not for real sensitive communication.
    EOS
  end

  test do
    assert_match "gorz local prototype CLI", shell_output("#{bin}/gorz help")
  end
end
