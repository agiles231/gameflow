# Noncreative mesh integration

Preserve the original Meshy download or existing source. Work on a derived copy. Allowed operations are those necessary to deliver the asset unchanged in appearance to the destination: format conversion, declared unit/axis/orientation/pivot adjustment, selecting export objects, resolving texture paths, and connecting supplied maps to the established engine material contract. Record these settings so reimport is reproducible.

Do not sculpt, remodel anatomy, retopologize, change silhouette, repaint textures, redesign materials, or perform creative cleanup. Do not add topology, UV, manifoldness, texel-density or artistic audits to ordinary Meshy delivery. If a file fails to decode or import, diagnose that delivery failure with the minimum relevant inspection and report the blocker or a permitted technical correction.

Local mesh creation is allowed only for an explicitly identified simple shape such as a primitive greybox cube or plane. Record the exception and intended use in the task. A complex object assembled from scripted primitives is still a complex mesh and must use Meshy MCP. Do not silently substitute a simple placeholder for a requested final complex asset.

Required engine material hookups may set supplied channels, normal-map conventions and color-space flags. Preserve the delivered imagery; do not bake a creative replacement or improve its appearance on your own. Validate that dependencies resolve after reopening/importing. User-requested deeper review must be a separately scoped explicit criterion.
