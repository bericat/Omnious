Shader "Ominous/Video Lit"
{
    Properties
    {
        _BaseMap ("Textura", 2D) = "white" {}
        _BaseColor ("Color", Color) = (1,1,1,1)
        _EmissionColor ("Emisión", Color) = (0,0,0,1)
        _AmbientBoost ("Ambiente extra (exterior)", Float) = 1
        _Exterior ("Niebla de exterior", Float) = 0
        _RoomAO ("Oscurecer junto a suelo y techo", Float) = 0
        _Sheen ("Brillo discreto", Range(0, 1)) = 0
        _Detile ("Romper repetición (superficies)", Range(0, 1)) = 0
    }
    SubShader
    {
        Tags { "RenderType"="Opaque" "RenderPipeline"="UniversalPipeline" "Queue"="Geometry" }
        HLSLINCLUDE
        #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
        CBUFFER_START(UnityPerMaterial)
            float4 _BaseMap_ST;
            half4 _BaseColor;
            half4 _EmissionColor;
            float _AmbientBoost;
            float _Exterior;
            float _RoomAO;
            float _Sheen;
            float _Detile;
        CBUFFER_END
        // Ruido de valor en el espacio del mundo: varía las superficies grandes sin costuras.
        float DetileHash(float3 p) { p = frac(p * 0.3183099 + 0.1); p *= 17.0; return frac(p.x * p.y * p.z * (p.x + p.y + p.z)); }
        float DetileNoise(float3 x)
        {
            float3 i = floor(x); float3 f = frac(x); f = f * f * (3.0 - 2.0 * f);
            return lerp(lerp(lerp(DetileHash(i), DetileHash(i + float3(1,0,0)), f.x), lerp(DetileHash(i + float3(0,1,0)), DetileHash(i + float3(1,1,0)), f.x), f.y),
                        lerp(lerp(DetileHash(i + float3(0,0,1)), DetileHash(i + float3(1,0,1)), f.x), lerp(DetileHash(i + float3(0,1,1)), DetileHash(i + float3(1,1,1)), f.x), f.y), f.z);
        }
        ENDHLSL

        Pass
        {
            Name "ForwardLit"
            Tags { "LightMode"="UniversalForward" }
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile _ _ADDITIONAL_LIGHTS _ADDITIONAL_LIGHTS_VERTEX
            #pragma multi_compile _ _CLUSTER_LIGHT_LOOP
            #pragma multi_compile_fragment _ _ADDITIONAL_LIGHT_SHADOWS
            #pragma multi_compile_fragment _ _SHADOWS_SOFT _SHADOWS_SOFT_LOW _SHADOWS_SOFT_MEDIUM _SHADOWS_SOFT_HIGH
            #pragma multi_compile _ LIGHTMAP_ON
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            TEXTURE2D(_BaseMap); SAMPLER(sampler_BaseMap);
            half4 _Video_Ambient;
            half4 _Video_FogColor;
            half4 _Video_ExteriorFogColor;
            float4 _Video_Fog;         // x-y: niebla interior, inicio y fin
            float4 _Video_ExteriorFog; // x-y: niebla exterior, inicio y fin

            struct Attributes { float4 positionOS : POSITION; float3 normalOS : NORMAL; float2 uv : TEXCOORD0; float2 uvLightmap : TEXCOORD1; };
            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv : TEXCOORD0;
                float3 positionWS : TEXCOORD1;
                float3 normalWS : TEXCOORD2;
                float2 uvLightmap : TEXCOORD3;
            };

            Varyings Vert(Attributes i)
            {
                Varyings o;
                o.positionWS = TransformObjectToWorld(i.positionOS.xyz);
                o.normalWS = TransformObjectToWorldNormal(i.normalOS);
                o.positionCS = TransformWorldToHClip(o.positionWS);
                o.uv = TRANSFORM_TEX(i.uv, _BaseMap);
                o.uvLightmap = i.uvLightmap * unity_LightmapST.xy + unity_LightmapST.zw;
                return o;
            }

            half3 Sheen(float3 n, float3 v, float3 l, half3 color)
            {
                float3 h = normalize(l + v);
                return color * pow(saturate(dot(n, h)), 28.0) * _Sheen;
            }

            half4 Frag(Varyings i) : SV_Target
            {
                half3 tex = SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, i.uv).rgb;
                if (_Detile > 0.001)
                {
                    // Mezcla la textura con una copia girada y a otra escala según una máscara de ruido grande,
                    // y varía un poco el tono: el ojo deja de ver la misma mancha repetida cada metro.
                    float2 uv2 = float2(i.uv.y, -i.uv.x) * 0.61 + float2(0.37, 0.71);
                    half3 tex2 = SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, uv2).rgb;
                    float mask = smoothstep(0.3, 0.7, DetileNoise(i.positionWS * 0.55));
                    tex = lerp(tex, tex2, mask * _Detile);
                    tex *= lerp(1.0, lerp(0.82, 1.12, DetileNoise(i.positionWS * 0.21 + 7.3)), _Detile);
                }
                half3 albedo = tex * _BaseColor.rgb;
                float3 n = normalize(i.normalWS);
                float3 v = normalize(GetCameraPositionWS() - i.positionWS);
                // Ambiente desigual: entra algo más de luz desde arriba que desde abajo.
                #if defined(LIGHTMAP_ON)
                // Luz horneada: entra por las ventanas y deja los rincones oscuros.
                half3 light = SampleLightmap(i.uvLightmap, n) + _Video_Ambient.rgb * (0.72 + 0.28 * n.y);
                #else
                half3 light = _Video_Ambient.rgb * _AmbientBoost * (0.72 + 0.28 * n.y);
                #endif
                half3 spec = 0;

                #if defined(_ADDITIONAL_LIGHTS) || defined(_CLUSTER_LIGHT_LOOP)
                InputData inputData = (InputData)0;
                inputData.positionWS = i.positionWS;
                inputData.normalWS = n;
                inputData.normalizedScreenSpaceUV = GetNormalizedScreenSpaceUV(i.positionCS);
                uint pixelLightCount = GetAdditionalLightsCount();
                LIGHT_LOOP_BEGIN(pixelLightCount)
                    Light l = GetAdditionalLight(lightIndex, i.positionWS, half4(1,1,1,1));
                    half3 c = l.color * l.distanceAttenuation * l.shadowAttenuation;
                    light += c * saturate(dot(n, l.direction));
                    spec += Sheen(n, v, l.direction, c);
                LIGHT_LOOP_END
                #endif

                if (_RoomAO > 0.5)
                {
                    float edge = saturate(min(i.positionWS.y / 0.5, (2.6 - i.positionWS.y) / 0.5));
                    light *= lerp(0.55, 1.0, edge);
                }

                half3 color = albedo * light + spec + _EmissionColor.rgb * tex;
                float d = distance(i.positionWS, GetCameraPositionWS());
                if (_Exterior > 0.5)
                {
                    float fog = saturate((d - _Video_ExteriorFog.x) / max(0.001, _Video_ExteriorFog.y - _Video_ExteriorFog.x));
                    fog = 1.0 - (1.0 - fog) * (1.0 - fog); // cierra antes, como niebla real
                    color = lerp(color, _Video_ExteriorFogColor.rgb, fog);
                }
                else
                {
                    float fog = saturate((d - _Video_Fog.x) / max(0.001, _Video_Fog.y - _Video_Fog.x));
                    color = lerp(color, _Video_FogColor.rgb, fog);
                }
                return half4(color, 1);
            }
            ENDHLSL
        }

        Pass
        {
            Name "ShadowCaster"
            Tags { "LightMode"="ShadowCaster" }
            ZWrite On
            ZTest LEqual
            ColorMask 0
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile_vertex _ _CASTING_PUNCTUAL_LIGHT_SHADOW
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Shadows.hlsl"
            float3 _LightDirection;
            float3 _LightPosition;
            float4 Vert(float4 p : POSITION, float3 normal : NORMAL) : SV_POSITION
            {
                float3 ws = TransformObjectToWorld(p.xyz);
                float3 ns = TransformObjectToWorldNormal(normal);
                #if _CASTING_PUNCTUAL_LIGHT_SHADOW
                float3 dir = normalize(_LightPosition - ws);
                #else
                float3 dir = _LightDirection;
                #endif
                float4 c = TransformWorldToHClip(ApplyShadowBias(ws, ns, dir));
                #if UNITY_REVERSED_Z
                c.z = min(c.z, UNITY_NEAR_CLIP_VALUE);
                #else
                c.z = max(c.z, UNITY_NEAR_CLIP_VALUE);
                #endif
                return c;
            }
            half Frag() : SV_Target { return 0; }
            ENDHLSL
        }

        Pass
        {
            Name "Meta"
            Tags { "LightMode"="Meta" }
            Cull Off
            HLSLPROGRAM
            #pragma vertex UniversalVertexMeta
            #pragma fragment Frag
            #pragma shader_feature EDITOR_VISUALIZATION
            TEXTURE2D(_BaseMap); SAMPLER(sampler_BaseMap);
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/UniversalMetaPass.hlsl"
            half4 Frag(Varyings i) : SV_Target
            {
                half3 tex = SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, i.uv).rgb;
                MetaInput m = (MetaInput)0;
                m.Albedo = tex * _BaseColor.rgb;
                m.Emission = _EmissionColor.rgb * tex;
                return UniversalFragmentMeta(i, m);
            }
            ENDHLSL
        }

        Pass
        {
            Name "DepthOnly"
            Tags { "LightMode"="DepthOnly" }
            ZWrite On
            ColorMask R
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            float4 Vert(float4 p : POSITION) : SV_POSITION { return TransformObjectToHClip(p.xyz); }
            half Frag() : SV_Target { return 0; }
            ENDHLSL
        }
    }
}
