# Deferred production

Rigging and animation are deferred in this version of the workflow. Do not create or repair skeletons, skinning, actions, clips, retargeting, animation graphs or playback production, through Blender, Meshy, Unreal or another provider.

Preserve existing artifacts. Record affected work as `deferred` with its reason, dependencies and explicit reactivation condition. Skip it in autonomous selection. Deferred tasks must have no dependents. Combine rigging and animation into one deferred leaf per asset depending on its delivered static mesh; explicitly rescope active contracts before removing any conflicting dependency edges and record the rationale. A connected provider or newly discovered tool does not reactivate it. Only explicit user direction to revise the policy can do so.
