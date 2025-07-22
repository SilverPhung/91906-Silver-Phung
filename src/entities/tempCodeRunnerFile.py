if self.state == PlayerState.IDLE:
            # Try to use the specific idle animation for this weapon
            idle_anim = f"Idle_{weapon_name.lower()}"
            Debug.update("Trying Idle Animation", idle_anim)

            if idle_anim in self.animations and (
                self.animations[idle_anim].get("sequence")
                or self.animations[idle_anim].get("idle")
            ):
                self.set_animation(idle_anim)
            else:
                # If specific idle animation not found, try generic weapon idle
                # Check for matching weapon types with different case formats
                found = False
                for anim_name in self.animations:
                    if (
                        anim_name.startswith("Idle_")
                        and weapon_name.lower() in anim_name.lower()
                    ):
                        self.set_animation(anim_name)
                        found = True
                        break

                # If still not found, use any available idle animation as last resort
                if not found:
                    Debug.update("Fallback Animation", "Using first available idle")
                    weapon_priority = [
                        self.current_weapon.value
                    ]
                    for weapon in WeaponType:
                        if weapon != self.current_weapon:
                            weapon_priority.append(weapon.value)

                    for weapon_type in weapon_priority:
                        idle_check = f"Idle_{weapon_type.lower()}"
                        if idle_check in self.animations and (
                            self.animations[idle_check].get("sequence")
                            or self.animations[idle_check].get("idle")
                        ):
                            self.set_animation(idle_check)
                            found = True
                            break

                    # Last resort - use any idle animation
                    if not found:
                        for anim_name in self.animations:
                            if anim_name.startswith("Idle_"):
                                self.set_animation(anim_name)
                                break

        elif self.state == PlayerState.WALKING:
            # Try exact match first
            walk_anim = f"Walk_{weapon_name.lower()}"

            # Then try alternative cases
            if not (
                walk_anim in self.animations
                and (
                    self.animations[walk_anim].get("sequence")
                    or self.animations[walk_anim].get("idle")
                )
            ):
                for anim_name in self.animations:
                    if (
                        anim_name.startswith("Walk_")
                        and weapon_name.lower() in anim_name.lower()
                    ):
                        walk_anim = anim_name
                        break

            if walk_anim in self.animations and (
                self.animations[walk_anim].get("sequence")
                or self.animations[walk_anim].get("idle")
            ):
                self.set_animation(walk_anim)
            else:
                # Fallback to any walk animation
                for anim_name in self.animations:
                    if anim_name.startswith("Walk_"):
                        self.set_animation(anim_name)
                        break

        elif self.state == PlayerState.SHOOTING:
            shoot_anim = "Gun_Shot"
            if shoot_anim in self.animations and (
                self.animations[shoot_anim].get("sequence")
                or self.animations[shoot_anim].get("idle")
            ):
                # Only set animation if not already shooting or if current animation is not the full shooting cycle
                if (
                    self.current_animation != shoot_anim
                    or self.current_animation == shoot_anim
                    and self.current_animation_frame
                    == len(self.animations[shoot_anim]["sequence"]) - 1
                ):
                    self.set_animation(shoot_anim)

        elif self.state == PlayerState.ATTACKING:
            # Try to use the specific attack animation for this weapon
            if weapon_name in self.animations and (
                self.animations[weapon_name].get("sequence")
                or self.animations[weapon_name].get("idle")
            ):
                # Only set animation if not already attacking or if current animation is not the full attack cycle
                if (
                    self.current_animation != weapon_name
                    or self.current_animation == weapon_name
                    and self.current_animation_frame
                    == len(self.animations[weapon_name]["sequence"]) - 1
                ):
                    self.set_animation(weapon_name)
            else:
                # Try to find a matching attack animation
                for anim_name in self.animations:
                    if (
                        anim_name.startswith("Walk_")
                        and weapon_name.lower() in anim_name.lower()
                    ):
                        walk_anim = anim_name
                        break

            if walk_anim in self.animations and (
                self.animations[walk_anim].get("sequence")
                or self.animations[walk_anim].get("idle")
            ):
                self.set_animation(walk_anim)
            else:
                # Fallback to any walk animation
                for anim_name in self.animations:
                    if anim_name.startswith("Walk_"):
                        self.set_animation(anim_name)
                        break

        elif self.state == PlayerState.DYING:
            if "Death" in self.animations and (
                self.animations["Death"].get("sequence")
                or self.animations["Death"].get("idle")
            ):
                self.set_animation("Death")